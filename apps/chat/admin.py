from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'sent_at', 'is_read']
    can_delete = True


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'last_message_at', 'is_read_by_admin', 'is_read_by_user']
    list_filter = ['is_read_by_admin', 'is_read_by_user', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'last_message_at']
    inlines = [MessageInline]
    
    def get_unread_count(self, obj):
        return obj.messages.filter(is_read=False).count()
    get_unread_count.short_description = 'Messages non lus'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'content_preview', 'sent_at', 'is_read']
    list_filter = ['is_read', 'sent_at', 'sender']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['conversation', 'sender', 'content', 'sent_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Contenu'
