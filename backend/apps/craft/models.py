from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from apps.business.models import Business
from apps.designs.models import Design

User = get_user_model()

class PhysicalStamp(BaseModel):
    """مدل مهر فیزیکی (چوبی یا لیزری)"""
    STAMP_TYPE_CHOICES = (
        ('wood', _('مهر چوبی')),
        ('laser', _('حکاکی لیزری')),
    )
    
    STATUS_CHOICES = (
        ('active', _('فعال')),
        ('damaged', _('آسیب دیده')),
        ('retired', _('بازنشسته')),
    )
    
    name = models.CharField(max_length=255, verbose_name=_("نام مهر"))
    stamp_type = models.CharField(max_length=20, choices=STAMP_TYPE_CHOICES, verbose_name=_("نوع مهر"))
    design = models.ForeignKey(Design, on_delete=models.PROTECT, related_name='craft_physical_stamps', verbose_name=_("طرح"))
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='craft_physical_stamps', verbose_name=_("کسب‌وکار"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name=_("وضعیت"))
    
    dimensions = models.CharField(max_length=100, verbose_name=_("ابعاد"))
    material = models.CharField(max_length=100, verbose_name=_("جنس"))
    production_date = models.DateField(verbose_name=_("تاریخ ساخت"), null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True, verbose_name=_("آخرین استفاده"))
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد استفاده"))
    
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))
    
    class Meta:
        verbose_name = _("مهر فیزیکی")
        verbose_name_plural = _("مهرهای فیزیکی")
        ordering = ['-created_at']
        unique_together = ['business', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_stamp_type_display()})"

class RequestPhysicalStamp(BaseModel):
    """مدل درخواست ساخت مهر فیزیکی"""
    STATUS_CHOICES = (
        ('pending', _('در انتظار بررسی')),
        ('approved', _('تأیید شده')),
        ('in_progress', _('در حال ساخت')),
        ('completed', _('تکمیل شده')),
        ('rejected', _('رد شده')),
        ('cancelled', _('لغو شده')),
    )
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='craft_stamp_requests', verbose_name=_("کسب‌وکار"))
    design = models.ForeignKey(Design, on_delete=models.PROTECT, related_name='craft_stamp_requests', verbose_name=_("طرح"))
    stamp_type = models.CharField(max_length=20, choices=PhysicalStamp.STAMP_TYPE_CHOICES, verbose_name=_("نوع مهر"))
    
    dimensions = models.CharField(max_length=100, verbose_name=_("ابعاد درخواستی"))
    material = models.CharField(max_length=100, verbose_name=_("جنس درخواستی"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("تعداد"))
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    notes = models.TextField(blank=True, verbose_name=_("توضیحات"))
    
    # اطلاعات تکمیلی
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_craft_stamp_requests', verbose_name=_("تأیید کننده"))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تأیید"))
    estimated_completion = models.DateField(null=True, blank=True, verbose_name=_("تاریخ تخمینی تکمیل"))
    actual_completion = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تکمیل واقعی"))
    
    class Meta:
        verbose_name = _("درخواست مهر فیزیکی")
        verbose_name_plural = _("درخواست‌های مهر فیزیکی")
        ordering = ['-created_at']

    def __str__(self):
        return f"درخواست {self.stamp_type} برای {self.business.name}"
