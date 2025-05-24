from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from apps.core.models import BaseModel, ThumbnailMixin
from django.contrib.auth import get_user_model
from apps.core.utils import log_error, to_jalali
from django.utils import timezone
from django.db.models import SET_NULL
from apps.print_locations.models import PrintLocation
from django.core.validators import FileExtensionValidator

User = get_user_model()

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("نام برچسب"))
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True, verbose_name=_("اسلاگ"))

    def __str__(self):
        return self.name

    @property
    def designs_count(self):
        return self.designs.count()

    class Meta:
        verbose_name = _("برچسب")
        verbose_name_plural = _("برچسب‌ها")
        ordering = ['name']

class DesignCategory(BaseModel):
    """دسته‌بندی طرح‌ها"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_("نام دسته‌بندی"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("دسته‌بندی طرح")
        verbose_name_plural = _("دسته‌بندی‌های طرح")

class Family(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("نام خانواده"))
    slug = models.SlugField(max_length=280, unique=True, blank=True, null=True, verbose_name=_("اسلاگ"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    tags = models.ManyToManyField(Tag, blank=True, related_name='families', verbose_name=_("برچسب‌ها"))
    categories = models.ManyToManyField(DesignCategory, blank=True, related_name='families', verbose_name=_("دسته‌بندی‌ها"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخرین بروزرسانی"))
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))

    def __str__(self):
        return self.name

    @property
    def designs_count(self):
        return self.designs.count()

    class Meta:
        verbose_name = _("خانواده")
        verbose_name_plural = _("خانواده‌ها")
        ordering = ['-created_at']

class Design(BaseModel):
    """مدل طرح‌های گرافیکی"""
    STATUS_CHOICES = (
        ('draft', _('پیش‌نویس')),
        ('pending', _('در انتظار تأیید')),
        ('approved', _('تأیید شده')),
        ('rejected', _('رد شده')),
    )

    title = models.CharField(max_length=255, verbose_name=_("عنوان طرح"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    designer = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='designs', verbose_name=_("طراح"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='created_designs', verbose_name=_("ایجاد کننده"))
    
    file = models.FileField(
        upload_to='designs/files/',
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'ai', 'eps', 'pdf'])],
        verbose_name=_("فایل اصلی"),
        null=True, blank=True
    )
    preview_image = models.ImageField(
        upload_to='designs/previews/',
        verbose_name=_("تصویر پیش‌نمایش"),
        null=True, blank=True
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', 
                            verbose_name=_("وضعیت"))
    is_public = models.BooleanField(default=False, verbose_name=_("عمومی"))
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("قیمت (ریال)"))
    
    categories = models.ManyToManyField(DesignCategory, related_name='designs', 
                                      verbose_name=_("دسته‌بندی‌ها"))
    
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد بازدید"))
    downloads_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد دانلود"))

    def save(self, *args, **kwargs):
        if not self.created_by_id and hasattr(self, '_current_user'):
            self.created_by = self._current_user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("طرح")
        verbose_name_plural = _("طرح‌ها")
        ordering = ['-created_at']

class FamilyDesignRequirement(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='design_requirements', verbose_name=_("خانواده"))
    design_type = models.CharField(max_length=100, verbose_name=_("نوع طرح"))
    quantity = models.PositiveIntegerField(verbose_name=_("تعداد"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    is_required = models.BooleanField(default=True, verbose_name=_("ضروری است"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))

    def __str__(self):
        return f"{self.family.name} - {self.design_type} x{self.quantity}"

    @property
    def fulfilled_count(self):
        return self.family.designs.filter(type=self.design_type).count()

    @property
    def is_fulfilled(self):
        return self.fulfilled_count >= self.quantity

    class Meta:
        verbose_name = _("نیاز طراحی خانواده")
        verbose_name_plural = _("نیازهای طراحی خانواده‌ها")
        ordering = ['family', 'design_type']

class DesignFamily(models.Model):
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='design_families', verbose_name=_("طرح"))
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name='design_families', verbose_name=_("خانواده"))
    position = models.PositiveIntegerField(default=0, verbose_name=_("موقعیت"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))

    def __str__(self):
        return f"{self.design.title} در {self.family.name}"

    class Meta:
        verbose_name = _("طرح-خانواده")
        verbose_name_plural = _("طرح‌های-خانواده‌ها")
        ordering = ['family', 'position']
        unique_together = ('design', 'family')
