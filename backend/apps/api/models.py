from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class APIKey(BaseModel):
    """مدل کلید API برای دسترسی به APIهای سیستم"""
    name = models.CharField(max_length=100, verbose_name=_("نام کلید"))
    key = models.CharField(max_length=64, unique=True, verbose_name=_("کلید"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys', verbose_name=_("کاربر"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاریخ انقضا"))
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name=_("آخرین استفاده"))
    
    # محدودیت‌های دسترسی
    allowed_ips = models.TextField(blank=True, verbose_name=_("IP های مجاز"), 
                                 help_text=_("هر IP در یک خط"))
    rate_limit = models.PositiveIntegerField(default=1000, verbose_name=_("محدودیت تعداد درخواست"),
                                           help_text=_("تعداد درخواست مجاز در روز"))
    
    class Meta:
        verbose_name = _("کلید API")
        verbose_name_plural = _("کلیدهای API")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def is_expired(self):
        """بررسی انقضای کلید"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def update_last_used(self):
        """به‌روزرسانی زمان آخرین استفاده"""
        from django.utils import timezone
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])

class APILog(BaseModel):
    """مدل لاگ درخواست‌های API"""
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    )

    api_key = models.ForeignKey(APIKey, on_delete=models.SET_NULL, null=True, related_name='logs', verbose_name=_("کلید API"))
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_logs', verbose_name=_("کاربر"))
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, verbose_name=_("متد"))
    path = models.CharField(max_length=255, verbose_name=_("مسیر"))
    query_params = models.TextField(blank=True, verbose_name=_("پارامترهای درخواست"))
    request_body = models.TextField(blank=True, verbose_name=_("بدنه درخواست"))
    response_code = models.PositiveIntegerField(verbose_name=_("کد پاسخ"))
    response_body = models.TextField(blank=True, verbose_name=_("بدنه پاسخ"))
    ip_address = models.GenericIPAddressField(verbose_name=_("آدرس IP"))
    execution_time = models.FloatField(verbose_name=_("زمان اجرا (ثانیه)"))
    
    class Meta:
        verbose_name = _("لاگ API")
        verbose_name_plural = _("لاگ‌های API")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.method} {self.path} - {self.response_code}"
