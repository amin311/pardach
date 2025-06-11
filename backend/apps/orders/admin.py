from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order, OrderDetail, OrderItem, PrintProcess, OrderAssignment, OrderStatusHistory

class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1
    readonly_fields = ['total_price']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['total_price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """کلاس برای مدیریت سفارش‌ها در پنل ادمین"""
    list_display = ['id', 'customer', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'customer__email', 'id']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderDetailInline]

@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ['order', 'template', 'size', 'quantity', 'total_price']
    list_filter = ['size', 'fabric', 'print_type']
    search_fields = ['order__id', 'template__name']
    readonly_fields = ['total_price']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """کلاس برای مدیریت آیتم‌های سفارش در پنل ادمین"""
    list_display = ['order_detail', 'design', 'print_location', 'total_price']
    list_filter = ['print_location']
    search_fields = ['order_detail__order__id', 'design__title']
    readonly_fields = ['total_price']

@admin.register(PrintProcess)
class PrintProcessAdmin(admin.ModelAdmin):
    list_display = ('order', 'stage', 'business_responsible', 'status')
    list_filter = ('stage', 'status')
    search_fields = ('order__id', 'stage')
    raw_id_fields = ('order', 'business_responsible')

@admin.register(OrderAssignment)
class OrderAssignmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'business', 'process_type', 'status', 'deadline']
    list_filter = ['process_type', 'status', 'deadline']
    search_fields = ['order__id', 'business__name']
    readonly_fields = ['completed_at']

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'changed_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__id', 'changed_by__username']
    readonly_fields = ['created_at']
