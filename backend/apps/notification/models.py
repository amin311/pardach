from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.business.models import Business
from apps.core.utils import log_error, to_jalali
import uuid

class NotificationCategory(BaseModel):
    """دسته‌بندی اعلانات"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("نام دسته‌بندی"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("دسته‌بندی اعلان")
        verbose_name_plural = _("دسته‌بندی‌های اعلان")
        ordering = ['name']

class Notification(BaseModel):
    """مدل اعلان برای اطلاع‌رسانی رویدادها به کاربران"""
    TYPE_CHOICES = (
        ('order_status', _('وضعیت سفارش')),
        ('payment_status', _('وضعیت پرداخت')),
        ('business_activity', _('فعالیت کسب‌وکار')),
        ('system', _('سیستمی')),
        ('user', _('کاربری')),
        ('message', _('پیام')),
        ('order', _('سفارش')),
        ('payment', _('پرداخت')),
        ('other', _('سایر')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_("کاربر"))
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='system_notifications', verbose_name=_("کسب‌وکار"))
    category = models.ForeignKey(NotificationCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications', verbose_name=_("دسته‌بندی"))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_("نوع اعلان"))
    title = models.CharField(max_length=255, verbose_name=_("عنوان"))
    content = models.TextField(verbose_name=_("محتوا"))
    is_read = models.BooleanField(default=False, verbose_name=_("خوانده‌شده"))
    is_archived = models.BooleanField(default=False, verbose_name=_("آرشیو شده"))
    link = models.CharField(max_length=255, blank=True, verbose_name=_("لینک مرتبط"))
    priority = models.PositiveIntegerField(default=1, verbose_name=_("اولویت"))
    all_users = models.BooleanField(default=False, verbose_name=_("برای همه کاربران"))

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            log_error(f"Error saving notification {self.title}", e)
            raise

    def __str__(self):
        return f"اعلان: {self.title} برای {self.user.username}"

    class Meta:
        verbose_name = _("اعلان")
        verbose_name_plural = _("اعلان‌ها")
        ordering = ['-created_at']
