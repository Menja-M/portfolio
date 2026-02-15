from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone

from .models import Conversation, Message


def is_admin(user):
    """Check if user is admin (staff or superuser)"""
    return user.is_staff or user.is_superuser


@login_required
def chat_view(request):
    """
    Chat view for regular users.
    Users can send messages to the admin and see the conversation history.
    """
    # Get or create conversation for the user
    conversation, created = Conversation.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                content=content,
                sender=request.user
            )
            # Mark as unread for admin
            conversation.is_read_by_admin = False
            conversation.save()
            
            context = {'message': message, 'request': request}
            if request.htmx:
                return render(request, 'chat/partials/message.html', context)
    
    # Mark admin messages as read when user views the conversation
    Message.objects.filter(
        conversation=conversation,
        is_read=False
    ).exclude(sender=request.user).update(is_read=True)
    conversation.is_read_by_user = True
    conversation.save()
    
    messages = conversation.messages.all()
    return render(request, 'chat/home.html', {
        'conversation': conversation,
        'messages': messages
    })


@user_passes_test(is_admin)
def admin_inbox(request):
    """
    Admin inbox view - shows all conversations with unread counts.
    """
    conversations = Conversation.objects.all().order_by('-last_message_at')
    
    # Get unread count for each conversation
    for conv in conversations:
        conv.unread_count = conv.get_admin_unread_count()
    
    total_unread = sum(c.unread_count for c in conversations)
    
    return render(request, 'chat/admin/inbox.html', {
        'conversations': conversations,
        'total_unread': total_unread
    })


@user_passes_test(is_admin)
def admin_conversation(request, conversation_id):
    """
    Admin view for a specific conversation.
    Admin can read and reply to user messages.
    """
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            message = Message.objects.create(
                conversation=conversation,
                content=content,
                sender=request.user
            )
            # Mark as unread for user
            conversation.is_read_by_user = False
            conversation.save()
            
            context = {'message': message, 'request': request}
            if request.htmx:
                return render(request, 'chat/partials/message.html', context)
    
    # Mark user messages as read when admin views the conversation
    Message.objects.filter(
        conversation=conversation,
        is_read=False,
        sender=conversation.user
    ).update(is_read=True)
    conversation.is_read_by_admin = True
    conversation.save()
    
    messages = conversation.messages.all()
    
    return render(request, 'chat/admin/conversation.html', {
        'conversation': conversation,
        'messages': messages,
        'user': conversation.user
    })


@user_passes_test(is_admin)
def admin_conversation_list(request):
    """
    HTMX partial for conversation list (for real-time updates).
    """
    conversations = Conversation.objects.all().order_by('-last_message_at')
    for conv in conversations:
        conv.unread_count = conv.get_admin_unread_count()
    
    return render(request, 'chat/partials/conversation_list.html', {
        'conversations': conversations
    })