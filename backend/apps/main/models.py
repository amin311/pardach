from django.db import models
from apps.core.models import BaseModel

# Create your models here.

class Promotion(BaseModel):
    """
    مدل برای نمایش اسلایدهای تبلیغاتی در صفحه اصلی
    """
    title = models.CharField(max_length=100, verbose_name="عنوان")
    description = models.TextField(verbose_name="توضیحات", blank=True, null=True)
    image = models.ImageField(upload_to='promotions/', verbose_name="تصویر")
    link = models.CharField(max_length=200, verbose_name="لینک")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "تبلیغات"
        verbose_name_plural = "تبلیغات"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title


class MainPageSetting(BaseModel):
    """
    تنظیمات صفحه اصلی
    """
    key = models.CharField(max_length=100, unique=True, verbose_name="کلید")
    value = models.TextField(verbose_name="مقدار")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    class Meta:
        verbose_name = "تنظیم صفحه اصلی"
        verbose_name_plural = "تنظیمات صفحه اصلی"
        ordering = ['key']
    
    def __str__(self):
        return self.key
