from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.core.utils import log_error

User = get_user_model()

class Business(BaseModel):
    """مدل کسب‌وکار"""
    BUSINESS_TYPE_CHOICES = (
        ('manual_print', _('چاپ دستی')),
        ('digital_print', _('چاپ دیجیتال')),
        ('laser', _('حکاکی لیزری')),
        ('delivery', _('تحویل‌گیرنده')),
        ('set_design', _('ست‌بندی')),
        ('embroidery', _('گلدوزی')),
        ('other', _('سایر')),
    )

    STATUS_CHOICES = (
        ('pending', _('در انتظار تأیید')),
        ('active', _('فعال')),
        ('inactive', _('غیرفعال')),
    )

    name = models.CharField(max_length=255, verbose_name=_("نام کسب‌وکار"))
    slug = models.SlugField(max_length=280, unique=True, blank=True, verbose_name=_("اسلاگ"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    logo = models.ImageField(upload_to='business/logos/', blank=True, null=True, verbose_name=_("لوگو"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_businesses', verbose_name=_("مالک"))
    business_type = models.CharField(max_length=50, choices=BUSINESS_TYPE_CHOICES, default='manual_print', verbose_name=_("نوع کسب‌وکار"))
    address = models.TextField(verbose_name=_("آدرس"), blank=True, default="")
    phone = models.CharField(max_length=20, verbose_name=_("تلفن"), blank=True, default="")
    email = models.EmailField(verbose_name=_("ایمیل"), blank=True, default="")
    website = models.URLField(blank=True, verbose_name=_("وب‌سایت"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    services = models.JSONField(default=list, verbose_name=_("خدمات"))
    working_hours = models.JSONField(default=dict, verbose_name=_("ساعات کاری"))
    employees = models.ManyToManyField(User, through='EmployeeRole', related_name='employed_businesses', verbose_name=_("کارکنان"))
    allow_customer_info = models.BooleanField(default=False, verbose_name=_("اجازه دسترسی به اطلاعات مشتری"))

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
    ROLE_CHOICES = (
        ('admin', _('مدیر')),
        ('designer', _('طراح')),
        ('printer', _('چاپچی')),
        ('laser_operator', _('اپراتور لیزر')),
        ('embroidery_operator', _('اپراتور گلدوزی')),
        ('set_designer', _('ست‌بند')),
        ('delivery', _('پیک')),
        ('other', _('سایر')),
    )

    PAYMENT_TYPE_CHOICES = (
        ('hourly', _('ساعتی')),
        ('daily', _('روزانه')),
        ('monthly', _('ماهانه')),
        ('percentage', _('درصدی')),
        ('project', _('پروژه‌ای')),
    )

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='employee_roles', verbose_name=_("کسب‌وکار"))
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_positions', verbose_name=_("کارمند"))
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name=_("نقش"))
    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES, verbose_name=_("نوع پرداخت"))
    payment_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("مبلغ پرداختی"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    start_date = models.DateField(auto_now_add=True, verbose_name=_("تاریخ شروع"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("تاریخ پایان"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_role_display()} در {self.business.name}"

    class Meta:
        verbose_name = _("نقش کارمند")
        verbose_name_plural = _("نقش‌های کارمندان")
        unique_together = ('business', 'employee', 'role')
