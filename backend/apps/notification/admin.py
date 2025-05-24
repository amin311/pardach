from django.contrib import admin
from .models import NotificationCategory, Notification
from django.utils.translation import gettext_lazy as _

@admin.register(NotificationCategory)
class NotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'business', 'type', 'category', 'is_read', 'is_archived', 'priority', 'created_at')
    search_fields = ('title', 'content', 'user__username', 'business__name', 'category__name')
    list_filter = ('type', 'is_read', 'is_archived', 'category', 'priority', 'created_at')
    fieldsets = (
        (None, {'fields': ('user', 'business', 'category', 'type', 'title', 'content')}),
        (_('ویژگی‌ها'), {'fields': ('is_read', 'is_archived', 'link', 'priority')}),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20 