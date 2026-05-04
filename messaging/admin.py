from django.contrib import admin
from .models import Message, ChatRoom, ChatMembership, ChatMessage, MessageAttachment, ChatNotification, PinnedMessage


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'from_user', 'to_user', 'created_at', 'is_read')
    list_filter = ('is_read',)
    search_fields = ('subject', 'body', 'from_user__username', 'to_user__username')


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'created_by', 'created_at', 'is_archived')
    list_filter = ('type', 'is_archived')
    search_fields = ('title', 'description')


@admin.register(ChatMembership)
class ChatMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat', 'role_in_chat', 'joined_at', 'is_muted')
    list_filter = ('role_in_chat', 'is_muted')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'short_content', 'sent_at', 'is_edited', 'is_deleted')
    list_filter = ('is_edited', 'is_deleted')
    search_fields = ('content', 'sender__username')

    def short_content(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

    short_content.short_description = 'Текст'


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'message', 'file_type', 'file_size', 'uploaded_at')


@admin.register(ChatNotification)
class ChatNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'short_content', 'is_read', 'created_at')
    list_filter = ('type', 'is_read')

    def short_content(self, obj):
        return obj.content[:80] + '...' if len(obj.content) > 80 else obj.content

    short_content.short_description = 'Текст'


@admin.register(PinnedMessage)
class PinnedMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'message', 'pinned_by', 'pinned_at', 'is_active')
