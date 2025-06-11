from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.core.models import BaseModel
from django.conf import settings
from apps.orders.models import Order
import uuid
import jdatetime

User = get_user_model()

class Payment(BaseModel):
    """مدل پرداخت برای ذخیره اطلاعات پرداخت‌های کاربران"""
    
    STATUS_CHOICES = (
        ('pending', _('در انتظار')),
        ('successful', _('موفق')),
        ('failed', _('ناموفق')),
        ('cancelled', _('لغو شده')),
    )

    GATEWAY_CHOICES = (
        ('zarinpal', _('زرین‌پال')),
        ('idpay', _('آی‌دی پی')),
        ('internal', _('داخلی')),
    )

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='payments', 
        verbose_name=_("کاربر")
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='payments', 
        verbose_name=_("سفارش")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name=_("مبلغ (تومان)")
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        verbose_name=_("وضعیت")
    )
    transaction_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True, 
        verbose_name=_("شناسه تراکنش")
    )
    gateway = models.CharField(
        max_length=100, 
        choices=GATEWAY_CHOICES,
        default='zarinpal',
        verbose_name=_("درگاه پرداخت")
    )
    callback_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name=_("آدرس بازگشت")
    )
    description = models.TextField(
        blank=True, 
        verbose_name=_("توضیحات")
    )
    payment_data = models.JSONField(
        blank=True, 
        null=True, 
        verbose_name=_("داده‌های پرداخت")
    )

    def jalali_created_at(self):
        """تبدیل تاریخ ایجاد به شمسی"""
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')

    def jalali_updated_at(self):
        """تبدیل تاریخ بروزرسانی به شمسی"""
        return jdatetime.datetime.fromgregorian(datetime=self.updated_at).strftime('%Y/%m/%d %H:%M')

    def __str__(self):
        return f"پرداخت {self.id} - کاربر {self.user.username}"

    class Meta:
        verbose_name = _("پرداخت")
        verbose_name_plural = _("پرداخت‌ها")
        ordering = ['-created_at']


class Transaction(BaseModel):
    """مدل تراکنش برای ذخیره جزئیات تراکنش‌های هر پرداخت"""
    
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='transactions', 
        verbose_name=_("پرداخت")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name=_("مبلغ (تومان)")
    )
    status = models.CharField(
        max_length=20, 
        choices=Payment.STATUS_CHOICES, 
        default='pending', 
        verbose_name=_("وضعیت")
    )
    authority = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name=_("کد پیگیری درگاه")
    )
    ref_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name=_("کد مرجع تراکنش")
    )
    gateway_response = models.JSONField(
        blank=True, 
        null=True, 
        verbose_name=_("پاسخ درگاه")
    )

    def jalali_created_at(self):
        """تبدیل تاریخ ایجاد به شمسی"""
        return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')

    def __str__(self):
        return f"تراکنش {self.id} - پرداخت {self.payment.id}"

    class Meta:
        verbose_name = _("تراکنش")
        verbose_name_plural = _("تراکنش‌ها")
        ordering = ['-created_at']


class DesignerPayment(BaseModel):
    """
    مدل پرداخت به ست‌بندها و طراحان
    این مدل برای ثبت پرداخت‌های انجام شده به ست‌بندها و طراحان استفاده می‌شود
    """
    set_design = models.ForeignKey(
        "set_design.SetDesign",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name=_("ست‌بندی مرتبط")
    )
    designer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_payments",
        verbose_name=_("ست‌بند/طراح")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        verbose_name=_("مبلغ (تومان)")
    )
    payment_method = models.CharField(
        max_length=100,
        verbose_name=_("روش پرداخت")
    )
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("شناسه تراکنش")
    )
    is_paid = models.BooleanField(
        default=True,
        verbose_name=_("پرداخت شده")
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("تاریخ پرداخت")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("توضیحات")
    )
    
    def jalali_payment_date(self):
        """تبدیل تاریخ پرداخت به شمسی"""
        return jdatetime.datetime.fromgregorian(datetime=self.payment_date).strftime('%Y/%m/%d %H:%M')
    
    def __str__(self):
        return f"پرداخت #{self.id} به {self.designer.get_full_name()} - مبلغ: {self.amount} تومان"
    
    class Meta:
        verbose_name = _("پرداخت به طراح")
        verbose_name_plural = _("پرداخت‌های طراحان")
        ordering = ['-payment_date']
