from django.db import models
from django.utils.translation import gettext_lazy as _

class ClothingSection(models.Model):
    """بخش‌های فیزیکی لباس (آستین، پشت، جیب …)"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("نام بخش"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("کد بخش"))
    default_price_modifier = models.DecimalField(max_digits=6, decimal_places=2, default=0, verbose_name=_("ضریب قیمت"))
    class Meta:
        verbose_name = _("بخش لباس")
        verbose_name_plural = _("بخش‌های لباس")
    def __str__(self):
        return self.name

class RakebOrientation(models.TextChoices):
    INSIDE = "inside", _("به داخل")
    OUTSIDE = "outside", _("به بیرون") 