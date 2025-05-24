from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

class PrintLocation(BaseModel):
    """مدل بخش‌های مختلف لباس برای چاپ"""
    name = models.CharField(max_length=100, verbose_name=_("نام بخش"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    max_width = models.PositiveIntegerField(verbose_name=_("حداکثر عرض (سانتی‌متر)"))
    max_height = models.PositiveIntegerField(verbose_name=_("حداکثر ارتفاع (سانتی‌متر)"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    
    # محدودیت‌های چاپ
    supports_digital = models.BooleanField(default=True, verbose_name=_("پشتیبانی از چاپ دیجیتال"))
    supports_manual = models.BooleanField(default=True, verbose_name=_("پشتیبانی از چاپ دستی"))
    min_dpi = models.PositiveIntegerField(default=300, verbose_name=_("حداقل DPI تصویر"))
    
    class Meta:
        verbose_name = _("بخش لباس")
        verbose_name_plural = _("بخش‌های لباس")
        ordering = ['name']

    def __str__(self):
        return self.name 