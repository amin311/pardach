from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("نام نقش"))
    description = models.TextField(blank=True, null=True, verbose_name=_("توضیحات نقش"))
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("نقش")
        verbose_name_plural = _("نقش‌ها")

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15, unique=True, null=True, blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                   message=_("شماره تماس نامعتبر است."))],
        verbose_name=_("شماره تلفن")
    )
    is_verified = models.BooleanField(default=False, verbose_name=_("تأیید شده"))

    # فیلد تغییر کرده: نقش‌ها به صورت ManyToMany
    roles = models.ManyToManyField(Role, related_name='users', blank=True, verbose_name=_("نقش‌ها"))
    # نقش فعال فعلی کاربر
    current_role = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("نقش فعلی"))

    groups = models.ManyToManyField(
        'auth.Group', verbose_name=_('groups'), blank=True,
        related_name='custom_user_set', related_query_name='custom_user'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', verbose_name=_('user permissions'), blank=True,
        related_name='custom_user_set', related_query_name='custom_user'
    )

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")
        permissions = [
            ('view_dashboard', _("می‌تواند داشبورد را مشاهده کند")),
        ]

    def __str__(self):
        return self.username

User = CustomUser
