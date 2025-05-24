from django.contrib import admin
from .models import Payment, Transaction, DesignerPayment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """مدیریت پرداخت‌ها در پنل ادمین"""
    list_display = ('id', 'user', 'order', 'amount', 'status', 'gateway', 'created_at')
    list_filter = ('status', 'gateway', 'created_at')
    search_fields = ('user__username', 'user__email', 'order__id', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'transaction_id')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('user', 'order', 'amount', 'status', 'transaction_id')
        }),
        ('اطلاعات درگاه پرداخت', {
            'fields': ('gateway', 'callback_url', 'description', 'payment_data')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """مدیریت تراکنش‌ها در پنل ادمین"""
    list_display = ('id', 'payment', 'amount', 'status', 'authority', 'ref_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('payment__user__username', 'payment__user__email', 'authority', 'ref_id')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('payment', 'amount', 'status')
        }),
        ('اطلاعات تراکنش', {
            'fields': ('authority', 'ref_id', 'gateway_response')
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at',)
        })
    )

@admin.register(DesignerPayment)
class DesignerPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'designer', 'set_design', 'amount', 'payment_method', 'is_paid', 'payment_date']
    list_filter = ['is_paid', 'payment_date', 'payment_method']
    search_fields = ['designer__username', 'designer__first_name', 'designer__last_name', 'set_design__id']
    readonly_fields = ['created_at', 'updated_at', 'payment_date']
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('set_design', 'designer', 'amount', 'payment_method')
        }),
        ('وضعیت پرداخت', {
            'fields': ('is_paid', 'transaction_id', 'description')
        }),
        ('تاریخ و زمان', {
            'fields': ('payment_date', 'created_at', 'updated_at')
        }),
    )
    raw_id_fields = ['set_design', 'designer']
