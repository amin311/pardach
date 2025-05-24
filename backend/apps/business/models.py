from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.core.utils import log_error

User = get_user_model()

class Business(BaseModel):
    """مدل کسب‌وکار"""
    STATUS_CHOICES = (
        ('pending', _('در انتظار تأیید')),
        ('active', _('فعال')),
        ('inactive', _('غیرفعال')),
    )

    name = models.CharField(max_length=255, unique=True, verbose_name=_("نام کسب‌وکار"))
    slug = models.SlugField(max_length=280, unique=True, blank=True, verbose_name=_("اسلاگ"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    logo = models.ImageField(upload_to='business/logos/', blank=True, verbose_name=_("لوگو"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_businesses', verbose_name=_("مالک"))

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
            original_slug = self.slug
            num = 1
            while Business.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            log_error(f"Error saving business {self.name}", e)
            raise

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("کسب‌وکار")
        verbose_name_plural = _("کسب‌وکارها")
        ordering = ['-created_at']

class BusinessUser(BaseModel):
    """مدل کاربران کسب‌وکار با نقش‌های مختلف"""
    ROLE_CHOICES = (
        ('manager', _('مدیر')),
        ('employee', _('کارمند')),
    )

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='users', verbose_name=_("کسب‌وکار"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_roles', verbose_name=_("کاربر"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', verbose_name=_("نقش"))

    def __str__(self):
        return f"{self.user.username} - {self.business.name} ({self.get_role_display()})"

    class Meta:
        verbose_name = _("کاربر کسب‌وکار")
        verbose_name_plural = _("کاربران کسب‌وکار")
        unique_together = ['business', 'user']
        ordering = ['-created_at']

class BusinessActivity(BaseModel):
    """مدل فعالیت‌های کسب‌وکار"""
    ACTIVITY_TYPE_CHOICES = (
        ('design_sale', _('فروش طرح')),
        ('design_purchase', _('خرید طرح')),
        ('order_created', _('ایجاد سفارش')),
        ('order_completed', _('تکمیل سفارش')),
        ('payment_received', _('دریافت پرداخت')),
        ('other', _('سایر')),
    )

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='activities', verbose_name=_("کسب‌وکار"))
    title = models.CharField(max_length=255, verbose_name=_("عنوان فعالیت"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPE_CHOICES, default='other', verbose_name=_("نوع فعالیت"))
    details = models.JSONField(null=True, blank=True, verbose_name=_("جزئیات"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    def __str__(self):
        return f"{self.business.name} - {self.title}"

    class Meta:
        verbose_name = _("فعالیت کسب‌وکار")
        verbose_name_plural = _("فعالیت‌های کسب‌وکار")
        ordering = ['-created_at']
