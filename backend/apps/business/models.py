from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.core.utils import log_error

User = get_user_model()

class Business(models.Model):
    """مدل کسب‌وکار"""
    PRINT = "print"
    LASER = "laser"
    SET_DESIGN = "set_design"
    DELIVERY = "delivery"

    BUSINESS_TYPE_CHOICES = (
        (PRINT, _("چاپ")),
        (LASER, _("حکاکی لیزری")),
        (SET_DESIGN, _("ست‌بندی")),
        (DELIVERY, _("تحویل")),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='owned_businesses', verbose_name=_("مالک"))
    name = models.CharField(max_length=255, verbose_name=_("نام کسب‌وکار"))
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPE_CHOICES, default=PRINT, verbose_name=_("نوع کسب‌وکار"))
    services = models.JSONField(blank=True, null=True, verbose_name=_("خدمات"))
    # کارمندان/نقش‌های اختصاص‌یافته به این کسب‌وکار
    employees = models.ManyToManyField(User, through='EmployeeRole',
                                       related_name='businesses', blank=True,
                                       verbose_name=_("کارمندان"))
    allow_customer_info = models.BooleanField(default=False,
                                              verbose_name=_("اجازه دسترسی به اطلاعات مشتری"))

    class Meta:
        verbose_name = _("کسب‌وکار")
        verbose_name_plural = _("کسب‌وکارها")

    def __str__(self):
        return self.name

class BusinessUser(BaseModel):
    """مدل کاربران کسب‌وکار با نقش‌های مختلف"""
    ROLE_CHOICES = (
        ('manager', _('مدیر')),
        ('employee', _('کارمند')),
    )

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='business_users', verbose_name=_("کسب‌وکار"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_memberships', verbose_name=_("کاربر"))
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

class EmployeeRole(models.Model):
    """مدل نقش کارکنان در کسب‌وکار"""
    # کسب‌وکاری که کاربر در آن کار می‌کند
    business = models.ForeignKey('Business', on_delete=models.CASCADE,
                                 related_name='employee_roles', verbose_name=_("کسب‌وکار"))
    # کاربر دارای این نقش
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='employee_roles', verbose_name=_("کاربر"))
    role = models.CharField(max_length=50, verbose_name=_("نقش"))
    PAYMENT_TYPE_CHOICES = (
        ('percentage', _("درصدی")),
        ('monthly', _("ماهیانه")),
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES,
                                    verbose_name=_("نوع پرداخت"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    class Meta:
        verbose_name = _("نقش کارمند")
        verbose_name_plural = _("نقش‌های کارمند")

    def __str__(self):
        return f"{self.user.username} - {self.role}"
