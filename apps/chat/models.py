from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """
    Conversation between a user and the admin (portfolio owner).
    Each user has one conversation with the admin.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)
    is_read_by_admin = models.BooleanField(default=True)  # Admin has read all messages
    is_read_by_user = models.BooleanField(default=True)   # User has read all messages

    def __str__(self):
        return f"Conversation with {self.user.username}"
    
    def get_admin_unread_count(self):
        """Returns count of messages not read by admin"""
        return self.messages.filter(is_read=False, sender=self.user).count()
    
    def get_user_unread_count(self):
        """Returns count of messages not read by user (from admin)"""
        return self.messages.filter(is_read=False).exclude(sender=self.user).count()


class Message(models.Model):
    """
    A message in a conversation.
    Can be sent by either the user or the admin.
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.username} at {self.sent_at}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update conversation's last_message_at
        self.conversation.last_message_at = self.sent_at
        self.conversation.save()
    
    @property
    def is_from_admin(self):
        """Check if message is from admin (staff/superuser)"""
        return self.sender.is_staff or self.sender.is_superuser
