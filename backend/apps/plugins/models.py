from django.db import models
from django.utils.translation import gettext_lazy as _

class Plugin(models.Model):
    """پایه ساده برای سیستم افزونه مانند وردپرس"""
    name = models.CharField(max_length=120, unique=True, verbose_name=_("نام افزونه"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    active = models.BooleanField(default=False, verbose_name=_("فعال؟"))
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = _("افزونه")
        verbose_name_plural = _("افزونه‌ها")
    def __str__(self):
        return self.name 