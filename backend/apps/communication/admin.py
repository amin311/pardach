from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Chat, Message, Notification

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_participants', 'business', 'created_at')
    search_fields = ('title', 'participants__username', 'business__name')
    list_filter = ('created_at',)
    fieldsets = (
        (None, {'fields': ('title', 'participants', 'business')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_participants(self, obj):
        return ', '.join([user.username for user in obj.participants.all()])
    get_participants.short_description = _("شرکت‌کنندگان")

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'content', 'is_read', 'created_at')
    search_fields = ('content', 'sender__username', 'chat__title')
    list_filter = ('is_read', 'created_at')
    fieldsets = (
        (None, {'fields': ('chat', 'sender', 'content', 'is_read')}),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'business', 'type', 'title', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'user__username', 'business__name')
    list_filter = ('type', 'is_read', 'created_at')
    fieldsets = (
        (None, {'fields': ('user', 'business', 'type', 'title', 'content', 'is_read', 'link')}),
    )
    readonly_fields = ('created_at', 'updated_at')
