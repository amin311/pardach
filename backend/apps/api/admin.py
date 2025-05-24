from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import APIKey, APILog

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'expires_at', 'last_used_at', 'created_at')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('name', 'key', 'user__username', 'user__email')
    readonly_fields = ('key', 'created_at', 'updated_at', 'last_used_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'key', 'user', 'is_active')
        }),
        (_('محدودیت‌ها'), {
            'fields': ('expires_at', 'allowed_ips', 'rate_limit')
        }),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at', 'last_used_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """تولید کلید API در صورت ایجاد جدید"""
        if not change:  # اگر در حال ایجاد کلید جدید هستیم
            import secrets
            obj.key = secrets.token_hex(32)  # تولید کلید 64 کاراکتری
        super().save_model(request, obj, form, change)

@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = ('method', 'path', 'api_key', 'user', 'response_code', 'execution_time', 'created_at')
    list_filter = ('method', 'response_code', 'created_at')
    search_fields = ('path', 'api_key__name', 'user__username', 'ip_address')
    readonly_fields = (
        'api_key', 'user', 'method', 'path', 'query_params', 'request_body',
        'response_code', 'response_body', 'ip_address', 'execution_time',
        'created_at', 'updated_at'
    )
    
    fieldsets = (
        (None, {
            'fields': ('api_key', 'user', 'method', 'path')
        }),
        (_('درخواست'), {
            'fields': ('query_params', 'request_body', 'ip_address')
        }),
        (_('پاسخ'), {
            'fields': ('response_code', 'response_body', 'execution_time')
        }),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # لاگ‌ها فقط به صورت خودکار ایجاد می‌شوند
    
    def has_change_permission(self, request, obj=None):
        return False  # لاگ‌ها قابل ویرایش نیستند
