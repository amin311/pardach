from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel

class PrintCenter(BaseModel):
    """مدل مکان‌های چاپ و تحویل"""
    name = models.CharField(max_length=100, verbose_name=_("نام مکان"))
    address = models.TextField(blank=True, null=True, verbose_name=_("آدرس"))
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("شهر"))
    phone = models.CharField(max_length=15, blank=True, verbose_name=_("تلفن"))
    opening_hours = models.CharField(max_length=200, blank=True, verbose_name=_("ساعت کاری"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    
    # اطلاعات تکمیلی
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("عرض جغرافیایی"))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name=_("طول جغرافیایی"))
    contact_person = models.CharField(max_length=100, blank=True, verbose_name=_("شخص رابط"))
    email = models.EmailField(blank=True, verbose_name=_("ایمیل"))
    
    class Meta:
        verbose_name = _("مکان چاپ")
        verbose_name_plural = _("مکان‌های چاپ")
        ordering = ['city', 'name']

    def __str__(self):
        city_name = self.city or "نامشخص"
        return f"{self.name} - {city_name}" 