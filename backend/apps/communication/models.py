from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import jdatetime
from django.contrib.auth import get_user_model

User = get_user_model()

class BaseModel(models.Model):
    """مدل پایه برای تمامی مدل‌های دیگر با فیلدهای مشترک"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("شناسه"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخرین بروزرسانی"))

    class Meta:
        abstract = True

    @property
    def created_at_jalali(self):
        """تبدیل تاریخ میلادی به شمسی"""
        if self.created_at:
            return jdatetime.datetime.fromgregorian(datetime=self.created_at).strftime('%Y/%m/%d %H:%M')
        return None

    @property
    def updated_at_jalali(self):
        """تبدیل تاریخ میلادی به شمسی"""
        if self.updated_at:
            return jdatetime.datetime.fromgregorian(datetime=self.updated_at).strftime('%Y/%m/%d %H:%M')
        return None

class Chat(BaseModel):
    """مدل چت برای ارتباط بین کاربران و کسب‌وکارها"""
    participants = models.ManyToManyField(User, related_name='chats', verbose_name=_("شرکت‌کنندگان"))
    business = models.ForeignKey(
        'business.Business', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='chats', 
        verbose_name=_("کسب‌وکار")
    )
    title = models.CharField(max_length=255, blank=True, verbose_name=_("عنوان چت"))

    def __str__(self):
        participants = ', '.join([user.username for user in self.participants.all()])
        return f"چت: {self.title or participants}"

    class Meta:
        verbose_name = _("چت")
        verbose_name_plural = _("چت‌ها")
        ordering = ['-created_at']

class Message(BaseModel):
    """مدل پیام برای محتوای ارسال شده در چت‌ها"""
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages', verbose_name=_("چت"))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name=_("فرستنده"))
    content = models.TextField(verbose_name=_("محتوای پیام"))
    is_read = models.BooleanField(default=False, verbose_name=_("خوانده‌شده"))

    def __str__(self):
        return f"پیام از {self.sender.username} در {self.chat}"

    class Meta:
        verbose_name = _("پیام")
        verbose_name_plural = _("پیام‌ها")
        ordering = ['created_at']

class Notification(BaseModel):
    """مدل اعلان برای اطلاع‌رسانی رویدادها به کاربران"""
    TYPE_CHOICES = (
        ('order_status', _('وضعیت سفارش')),
        ('payment_status', _('وضعیت پرداخت')),
        ('business_activity', _('فعالیت کسب‌وکار')),
        ('general', _('عمومی')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_("کاربر"))
    business = models.ForeignKey(
        'business.Business', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='comm_notifications', 
        verbose_name=_("کسب‌وکار")
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_("نوع اعلان"))
    title = models.CharField(max_length=255, verbose_name=_("عنوان"))
    content = models.TextField(verbose_name=_("محتوا"))
    is_read = models.BooleanField(default=False, verbose_name=_("خوانده‌شده"))
    link = models.CharField(max_length=255, blank=True, verbose_name=_("لینک مرتبط"))

    def __str__(self):
        return f"اعلان: {self.title} برای {self.user.username}"

    class Meta:
        verbose_name = _("اعلان")
        verbose_name_plural = _("اعلان‌ها")
        ordering = ['-created_at']
