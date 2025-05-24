from django.contrib import admin
from .models import Promotion, MainPageSetting

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'image', 'link')
        }),
        ('تنظیمات نمایش', {
            'fields': ('order', 'is_active')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MainPageSetting)
class MainPageSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('key', 'value', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات تنظیم', {
            'fields': ('key', 'value', 'description', 'is_active')
        }),
        ('اطلاعات سیستمی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
