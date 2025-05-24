from django.contrib import admin
from .models import Order, OrderItem
from django.utils.translation import gettext_lazy as _

class OrderItemInline(admin.TabularInline):
    """کلاس برای نمایش آیتم‌های سفارش در فرم سفارش"""
    model = OrderItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('design', 'quantity', 'unit_price', 'created_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """کلاس برای مدیریت سفارش‌ها در پنل ادمین"""
    list_display = ('id', 'customer', 'total_price', 'status', 'jalali_created_at', 'items_count')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'customer__email', 'customer_notes')
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_price', 'items_count')
    inlines = [OrderItemInline]
    fieldsets = (
        (None, {
            'fields': ('id', 'customer', 'total_price', 'status', 'customer_notes')
        }),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """کلاس برای مدیریت آیتم‌های سفارش در پنل ادمین"""
    list_display = ('id', 'order', 'design', 'quantity', 'unit_price', 'jalali_created_at')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'design__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('id', 'order', 'design', 'quantity', 'unit_price')
        }),
        (_('زمان‌ها'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
