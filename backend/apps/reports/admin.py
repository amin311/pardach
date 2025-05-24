from django.contrib import admin
from .models import ReportCategory, Report
from django.utils.translation import gettext_lazy as _

@admin.register(ReportCategory)
class ReportCategoryAdmin(admin.ModelAdmin):
    """پنل ادمین برای مدیریت دسته‌بندی‌های گزارش"""
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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """پنل ادمین برای مدیریت گزارش‌ها"""
    list_display = ('title', 'user', 'business', 'type', 'category', 'is_public', 'generated_at')
    search_fields = ('title', 'user__username', 'business__name')
    list_filter = ('type', 'category', 'is_public', 'generated_at')
    fieldsets = (
        (None, {'fields': ('user', 'business', 'category', 'type', 'title', 'data', 'is_public')}),
        (_('زمان‌ها'), {
            'fields': ('generated_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('generated_at', 'created_at', 'updated_at')
    list_per_page = 20
