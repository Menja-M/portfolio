import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat between users and admin.
    - Users connect to their own conversation channel
    - Admin connects to all conversations or specific conversation
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        
        # Reject connection if user is not authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Determine the group name based on user role
        if self.user.is_staff or self.user.is_superuser:
            # Admin joins the admin group (receives all messages)
            self.group_name = "chat_admin"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        else:
            # Regular user joins their specific conversation group
            self.conversation = await self.get_or_create_conversation()
            self.group_name = f"chat_conversation_{self.conversation.id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave the group
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        Expected format: {"message": "content", "conversation_id": id (for admin)}
        """
        data = json.loads(text_data)
        message_content = data.get('message', '').strip()
        
        if not message_content:
            return
        
        if self.user.is_staff or self.user.is_superuser:
            # Admin sending message to a specific user
            conversation_id = data.get('conversation_id')
            if conversation_id:
                await self.send_admin_message(conversation_id, message_content)
        else:
            # User sending message to admin
            await self.send_user_message(message_content)
    
    async def send_user_message(self, content):
        """User sends message to admin"""
        message = await self.create_message(self.conversation.id, self.user.id, content)
        
        # Send message to user's conversation group (so user sees their message)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': content,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'sender_is_admin': False,
                'message_id': message.id,
                'timestamp': str(message.sent_at),
            }
        )
        
        # Also send to admin group
        await self.channel_layer.group_send(
            "chat_admin",
            {
                'type': 'chat_message',
                'message': content,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'sender_is_admin': False,
                'conversation_id': self.conversation.id,
                'message_id': message.id,
                'timestamp': str(message.sent_at),
            }
        )
    
    async def send_admin_message(self, conversation_id, content):
        """Admin sends message to a specific user"""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return
        
        message = await self.create_message(conversation_id, self.user.id, content)
        
        # Send to the specific conversation group (for the user)
        group_name = f"chat_conversation_{conversation_id}"
        await self.channel_layer.group_send(
            group_name,
            {
                'type': 'chat_message',
                'message': content,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'sender_is_admin': True,
                'message_id': message.id,
                'timestamp': str(message.sent_at),
                'conversation_id': conversation_id,
            }
        )
        
        # Also send back to admin group so admin sees their own message
        await self.channel_layer.group_send(
            "chat_admin",
            {
                'type': 'chat_message',
                'message': content,
                'sender_id': self.user.id,
                'sender_name': self.user.username,
                'sender_is_admin': True,
                'message_id': message.id,
                'timestamp': str(message.sent_at),
                'conversation_id': conversation_id,
            }
        )
    
    async def chat_message(self, event):
        """
        Receive message from channel layer and send to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'sender_is_admin': event['sender_is_admin'],
            'message_id': event.get('message_id'),
            'timestamp': event.get('timestamp'),
            'conversation_id': event.get('conversation_id'),
        }))
    
    @database_sync_to_async
    def get_or_create_conversation(self):
        conversation, _ = Conversation.objects.get_or_create(user=self.user)
        return conversation
    
    @database_sync_to_async
    def get_conversation(self, conversation_id):
        try:
            return Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_message(self, conversation_id, sender_id, content):
        conversation = Conversation.objects.get(id=conversation_id)
        sender = User.objects.get(id=sender_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )
        return message