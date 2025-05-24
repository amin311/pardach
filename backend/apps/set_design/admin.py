from django.contrib import admin
from .models import SetDesign


@admin.register(SetDesign)
class SetDesignAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_item', 'designer', 'version', 'status', 'price', 'paid', 'created_at']
    list_filter = ['status', 'paid', 'created_at']
    search_fields = ['order_item__order__id', 'designer__username', 'designer__first_name', 'designer__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('order_item', 'designer', 'version', 'parent')
        }),
        ('فایل‌ها', {
            'fields': ('file', 'preview')
        }),
        ('وضعیت و پرداخت', {
            'fields': ('status', 'price', 'paid')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    raw_id_fields = ['order_item', 'designer', 'parent']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order_item', 'designer', 'parent') 