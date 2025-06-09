from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.core.utils import log_error

class UserManager(BaseUserManager):
    """مدیریت کاربران با امکان ایجاد کاربر عادی و ادمین"""
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError(_('نام کاربری الزامی است'))
        if not email:
            raise ValueError(_('ایمیل الزامی است'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """مدل سفارشی کاربر با پشتیبانی از نقش‌ها"""
    username = models.CharField(max_length=150, unique=True, verbose_name=_("نام کاربری"))
    email = models.EmailField(unique=True, verbose_name=_("ایمیل"))
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("نام خانوادگی"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    is_staff = models.BooleanField(default=False, verbose_name=_("کارمند"))
    current_role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='users', verbose_name=_("نقش فعلی"))
    
    # اصلاح تداخل با افزودن related_name به فیلدهای ارث‌بری‌شده
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def set_current_role(self, role_name):
        """تغییر نقش فعلی کاربر"""
        try:
            role = Role.objects.get(name=role_name)
            self.current_role = role
            self.save()
            return True
        except Role.DoesNotExist:
            log_error(f"Role {role_name} not found for user {self.username}")
            return False

    class Meta:
        verbose_name = _("کاربر")
        verbose_name_plural = _("کاربران")

class Role(models.Model):
    """مدل نقش‌ها برای مدیریت دسترسی‌ها"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("نام نقش"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name=_("مجوزها"),
        help_text=_("مجوزهای اختصاص‌یافته به این نقش")
    )

    def __str__(self):
        return self.name

    def get_permissions_list(self):
        """برگرداندن لیست نام مجوزها"""
        return list(self.permissions.values_list('codename', flat=True))

    class Meta:
        verbose_name = _("نقش")
        verbose_name_plural = _("نقش‌ها")
