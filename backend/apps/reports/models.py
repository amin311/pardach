from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from apps.business.models import Business
from apps.core.utils import log_error, to_jalali

User = get_user_model()

class ReportCategory(BaseModel):
    """دسته‌بندی گزارش‌ها"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("نام دسته‌بندی"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("دسته‌بندی گزارش")
        verbose_name_plural = _("دسته‌بندی‌های گزارش")
        ordering = ['name']

class Report(BaseModel):
    """مدل گزارش برای ثبت و نمایش گزارش‌های تحلیلی"""
    TYPE_CHOICES = (
        ('sales', _('فروش')),
        ('profit', _('سود')),
        ('user_activity', _('فعالیت کاربر')),
        ('business_performance', _('عملکرد کسب‌وکار')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports', verbose_name=_("کاربر"))
    business = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports', verbose_name=_("کسب‌وکار"))
    category = models.ForeignKey(ReportCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports', verbose_name=_("دسته‌بندی"))
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_("نوع گزارش"))
    title = models.CharField(max_length=255, verbose_name=_("عنوان"))
    data = models.JSONField(verbose_name=_("داده‌های گزارش"))
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ تولید"))
    is_public = models.BooleanField(default=False, verbose_name=_("عمومی"))

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            log_error(f"Error saving report {self.title}", e)
            raise

    def __str__(self):
        return f"گزارش: {self.title} برای {self.user.username}"

    class Meta:
        verbose_name = _("گزارش")
        verbose_name_plural = _("گزارش‌ها")
        ordering = ['-generated_at']
