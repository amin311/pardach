from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.html import mark_safe
from apps.core.models import BaseModel, ThumbnailMixin
from django.contrib.auth import get_user_model
from apps.designs.models import Tag, DesignCategory, Design
from apps.core.utils import log_error, to_jalali
from django.utils.text import slugify
from django.core.files import File
from PIL import Image
from io import BytesIO
import os
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from enum import Enum

User = get_user_model()

class Template(BaseModel, ThumbnailMixin):
    """مدل قالب برای نگهداری اطلاعات قالب‌های طراحی"""
    
    class Status(str, Enum):
        DRAFT = 'draft'
        PUBLISHED = 'published'
        FEATURED = 'featured'
        ARCHIVED = 'archived'

        @classmethod
        def choices(cls):
            return [(item.value, _(item.name.title())) for item in cls]

    STATUS_CHOICES = Status.choices()

    name = models.CharField(max_length=255, unique=True, verbose_name=_("نام قالب"))
    slug = models.SlugField(max_length=280, unique=True, blank=True, verbose_name=_("اسلاگ"))
    title = models.CharField(max_length=200, verbose_name=_("عنوان"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات قالب"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("قیمت قالب"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("قیمت با تخفیف"))
    discount_percent = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name=_("درصد تخفیف"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=Status.DRAFT, verbose_name=_("وضعیت"))
    is_premium = models.BooleanField(default=False, verbose_name=_("ویژه"))
    is_featured = models.BooleanField(default=False, verbose_name=_("برجسته"))
    view_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد بازدید"))
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد استفاده"))
    preview_image = models.ImageField(upload_to='templates/previews/', blank=True, verbose_name=_("تصویر پیش‌نمایش"))
    tags = models.ManyToManyField(Tag, blank=True, related_name='templates', verbose_name=_("برچسب‌ها"))
    categories = models.ManyToManyField(DesignCategory, blank=True, related_name='templates', verbose_name=_("دسته‌بندی‌ها"))
    similar_templates = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name=_("قالب‌های مشابه"))
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_templates', verbose_name=_("سازنده"))

    def save(self, *args, **kwargs):
        """ذخیره اطلاعات قالب با ایجاد اسلاگ و بهینه‌سازی تصویر پیش‌نمایش"""
        if not self.slug and self.name:
            self.slug = slugify(self.name)
            original_slug = self.slug
            num = 1
            while Template.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1

        if self.preview_image and not self.thumbnail:
            try:
                image = Image.open(self.preview_image)
                image.thumbnail((300, 300), Image.LANCZOS)
                thumb_io = BytesIO()
                image.save(thumb_io, 'JPEG', quality=85)
                thumbnail = File(thumb_io, name=f'thumb_{os.path.basename(self.preview_image.name)}')
                self.thumbnail.save(thumbnail.name, thumbnail, save=False)
            except Exception as e:
                log_error(f"Error creating thumbnail for template {self.name}", e)

        try:
            super().save(*args, **kwargs)
        except Exception as e:
            log_error(f"Error saving template {self.name}", e)
            raise

    def thumbnail_preview(self):
        """نمایش پیش‌نمایش تصویر برای استفاده در پنل ادمین"""
        if self.thumbnail:
            return mark_safe(f'<img src="{self.thumbnail.url}" width="100" />')
        elif self.preview_image:
            return mark_safe(f'<img src="{self.preview_image.url}" width="100" />')
        return "بدون تصویر"

    def increment_view_count(self):
        """افزایش شمارنده بازدید"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def increment_usage_count(self):
        """افزایش شمارنده استفاده"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])

    def is_discounted(self):
        """بررسی وجود تخفیف"""
        return self.discount_price is not None and self.discount_price < self.price

    def final_price(self):
        """محاسبه قیمت نهایی بر اساس تخفیف"""
        return self.discount_price if self.is_discounted() else self.price

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("قالب")
        verbose_name_plural = _("قالب‌ها")
        ordering = ['-created_at']

class Section(BaseModel):
    """مدل بخش برای تقسیم‌بندی هر قالب به بخش‌های مختلف"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='sections', verbose_name=_("قالب"))
    name = models.CharField(max_length=255, verbose_name=_("نام بخش"))
    slug = models.SlugField(max_length=280, blank=True, verbose_name=_("اسلاگ"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب نمایش بخش"))
    is_required = models.BooleanField(default=True, verbose_name=_("ضروری است"))
    unlimited_design_inputs = models.BooleanField(default=False, verbose_name=_("ورودی‌های نامحدود طرح"))
    max_design_inputs = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداکثر تعداد ورودی‌ها"))
    preview_image = models.ImageField(upload_to='sections/previews/', blank=True, verbose_name=_("تصویر پیش‌نمایش"))

    def save(self, *args, **kwargs):
        """ذخیره اطلاعات بخش با ایجاد اسلاگ یکتا"""
        if not self.slug and self.name:
            self.slug = slugify(self.name)
            original_slug = self.slug
            num = 1
            while Section.objects.filter(slug=self.slug, template=self.template).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{num}"
                num += 1
        try:
            super().save(*args, **kwargs)
        except Exception as e:
            log_error(f"Error saving section {self.name}", e)
            raise

    def __str__(self):
        return f"{self.template.name} - {self.name}"

    class Meta:
        verbose_name = _("بخش")
        verbose_name_plural = _("بخش‌ها")
        ordering = ['template', 'order']
        unique_together = ['template', 'slug']

class DesignInput(BaseModel):
    """مدل ورودی طرح برای تعیین مشخصات طرح‌های قابل استفاده در بخش"""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='design_inputs', verbose_name=_("بخش"))
    name = models.CharField(max_length=255, blank=True, verbose_name=_("نام ورودی"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب ورودی"))
    is_required = models.BooleanField(default=True, verbose_name=_("ضروری است"))
    default_design = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("طرح پیش‌فرض"))
    allowed_designs = models.ManyToManyField(Design, blank=True, related_name='allowed_in_inputs', verbose_name=_("طرح‌های مجاز"))
    allowed_categories = models.ManyToManyField(DesignCategory, blank=True, related_name='allowed_in_inputs', verbose_name=_("دسته‌بندی‌های مجاز"))
    allowed_tags = models.ManyToManyField(Tag, blank=True, related_name='allowed_in_inputs', verbose_name=_("برچسب‌های مجاز"))
    min_width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداقل عرض"))
    min_height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداقل ارتفاع"))
    max_width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداکثر عرض"))
    max_height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداکثر ارتفاع"))

    def __str__(self):
        return f"{self.section.name} - {self.name or f'ورودی {self.order}'}"

    class Meta:
        verbose_name = _("ورودی طرح")
        verbose_name_plural = _("ورودی‌های طرح")
        ordering = ['section', 'order']

class Condition(BaseModel):
    """مدل شرط برای تعیین شرایط و گزینه‌های انتخابی در بخش"""
    CONDITION_TYPE_CHOICES = (
        ('checkbox', _('چک‌باکس')),
        ('select', _('چند گزینه‌ای')),
        ('radio', _('تک انتخابی')),
        ('color', _('انتخاب رنگ')),
        ('number', _('عدد')),
        ('text', _('متن')),
    )

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='conditions', verbose_name=_("بخش"))
    name = models.CharField(max_length=255, verbose_name=_("نام شرط"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    condition_type = models.CharField(max_length=20, choices=CONDITION_TYPE_CHOICES, verbose_name=_("نوع شرط"))
    options = models.TextField(blank=True, help_text=_("برای چند گزینه‌ای، گزینه‌ها را با کاما جدا کنید."), verbose_name=_("گزینه‌ها"))
    default_value = models.CharField(max_length=255, blank=True, verbose_name=_("مقدار پیش‌فرض"))
    is_required = models.BooleanField(default=False, verbose_name=_("ضروری است"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("ترتیب نمایش"))
    affects_pricing = models.BooleanField(default=False, verbose_name=_("تأثیر بر قیمت"))
    price_factor = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_("ضریب قیمت"))

    def get_options_list(self):
        """دریافت لیست گزینه‌ها به صورت جداشده"""
        return [opt.strip() for opt in self.options.split(',')] if self.options else []

    def __str__(self):
        return f"{self.section.name} - {self.name}"

    class Meta:
        verbose_name = _("شرط")
        verbose_name_plural = _("شرایط")
        ordering = ['section', 'order']

class UserTemplate(BaseModel):
    """مدل قالب کاربر برای نگهداری پروژه‌های کاربران بر اساس قالب‌ها"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_templates', verbose_name=_("کاربر"))
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='user_templates', verbose_name=_("قالب"))
    name = models.CharField(max_length=255, blank=True, verbose_name=_("نام پروژه"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    is_completed = models.BooleanField(default=False, verbose_name=_("تکمیل شده"))
    final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("قیمت نهایی"))
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_("شناسه یکتا"))

    def calculate_final_price(self):
        """محاسبه قیمت نهایی بر اساس قیمت قالب و مقادیر انتخاب شده در شرایط"""
        base_price = self.template.final_price()
        extra_price = 0
        for user_section in self.user_sections.all():
            for user_condition in user_section.user_conditions.all():
                if user_condition.condition.affects_pricing and user_condition.value:
                    extra_price += float(user_condition.condition.price_factor)
        self.final_price = base_price + extra_price
        self.save(update_fields=['final_price'])
        return self.final_price

    def __str__(self):
        return self.name or f"{self.template.name} - {to_jalali(self.created_at)}"

    class Meta:
        verbose_name = _("قالب کاربر")
        verbose_name_plural = _("قالب‌های کاربر")
        ordering = ['-created_at']

class UserSection(BaseModel):
    """مدل بخش کاربر برای نگهداری اطلاعات بخش‌های انتخاب شده توسط کاربر"""
    user_template = models.ForeignKey(UserTemplate, on_delete=models.CASCADE, related_name='user_sections', verbose_name=_("قالب کاربر"))
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='user_sections', verbose_name=_("بخش"))
    is_completed = models.BooleanField(default=False, verbose_name=_("تکمیل شده"))

    def __str__(self):
        return f"{self.user_template} - {self.section.name}"

    class Meta:
        verbose_name = _("بخش کاربر")
        verbose_name_plural = _("بخش‌های کاربر")
        ordering = ['section__order']

class UserDesignInput(BaseModel):
    """مدل ورودی طرح کاربر برای نگهداری طرح‌های انتخاب شده توسط کاربر در هر بخش"""
    user_section = models.ForeignKey(UserSection, on_delete=models.CASCADE, related_name='user_design_inputs', verbose_name=_("بخش کاربر"))
    design_input = models.ForeignKey(DesignInput, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("ورودی طرح اصلی"))
    design = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("طرح انتخابی"))
    order = models.PositiveIntegerField(verbose_name=_("ترتیب ورودی"))

    def __str__(self):
        design_name = self.design.title if self.design else "بدون طرح"
        return f"{self.user_section} - ورودی {self.order} - {design_name}"

    class Meta:
        verbose_name = _("ورودی طرح کاربر")
        verbose_name_plural = _("ورودی‌های طرح کاربر")
        ordering = ['order']

class UserCondition(BaseModel):
    """مدل شرط کاربر برای نگهداری مقادیر انتخاب شده توسط کاربر برای هر شرط"""
    user_section = models.ForeignKey(UserSection, on_delete=models.CASCADE, related_name='user_conditions', verbose_name=_("بخش کاربر"))
    condition = models.ForeignKey(Condition, on_delete=models.CASCADE, verbose_name=_("شرط اصلی"))
    value = models.CharField(max_length=255, blank=True, verbose_name=_("مقدار انتخابی"))

    def __str__(self):
        value_display = self.value or "بدون مقدار"
        return f"{self.user_section} - {self.condition.name}: {value_display}"

    class Meta:
        verbose_name = _("شرط کاربر")
        verbose_name_plural = _("شرایط کاربر")
        ordering = ['condition__order']

class SetDimensions(BaseModel):
    """مدل ابعاد ست برای تعریف ابعاد استاندارد برای طرح‌ها"""
    name = models.CharField(max_length=100, verbose_name=_("نام"))
    width = models.FloatField(verbose_name=_("عرض"))
    height = models.FloatField(verbose_name=_("ارتفاع"))

    def __str__(self):
        return f"{self.name} ({self.width}x{self.height})"

    class Meta:
        verbose_name = _("ابعاد ست")
        verbose_name_plural = _("ابعاد ست‌ها")
        ordering = ['name']

class SectionRule(BaseModel):
    """مدل قوانین پذیرش طرح در هر بخش"""
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='rules', verbose_name=_("بخش"))
    name = models.CharField(max_length=100, verbose_name=_("نام قانون"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    
    # محدودیت‌های طرح
    min_width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداقل عرض"))
    max_width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداکثر عرض"))
    min_height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداقل ارتفاع"))
    max_height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداکثر ارتفاع"))
    min_dpi = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداقل DPI"))
    
    allowed_design_types = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("انواع طرح مجاز"),
        help_text=_("انواع طرح مجاز با کاما جدا شوند")
    )
    
    allowed_file_types = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("فرمت‌های فایل مجاز"),
        help_text=_("پسوندهای مجاز با کاما جدا شوند")
    )
    
    max_file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("حداکثر حجم فایل (KB)")
    )
    
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    
    class Meta:
        verbose_name = _("قانون بخش")
        verbose_name_plural = _("قوانین بخش")
        ordering = ['section', 'name']
        unique_together = ['section', 'name']

    def __str__(self):
        return f"{self.name} - {self.section.name}"

    def can_accept_design(self, design):
        """بررسی امکان پذیرش طرح با توجه به قوانین"""
        from PIL import Image
        import os
        
        # بررسی نوع طرح
        if self.allowed_design_types:
            allowed_types = [t.strip() for t in self.allowed_design_types.split(',')]
            if design.design_type not in allowed_types:
                return False, "نوع طرح مجاز نیست"
        
        # بررسی فرمت فایل
        if self.allowed_file_types:
            allowed_extensions = [ext.strip().lower() for ext in self.allowed_file_types.split(',')]
            file_ext = os.path.splitext(design.image.name)[1][1:].lower()
            if file_ext not in allowed_extensions:
                return False, "فرمت فایل مجاز نیست"
        
        # بررسی حجم فایل
        if self.max_file_size and design.image.size > self.max_file_size * 1024:
            return False, "حجم فایل بیش از حد مجاز است"
        
        try:
            # بررسی ابعاد و DPI تصویر
            with Image.open(design.image.path) as img:
                width, height = img.size
                
                if self.min_width and width < self.min_width:
                    return False, "عرض تصویر کمتر از حد مجاز است"
                if self.max_width and width > self.max_width:
                    return False, "عرض تصویر بیشتر از حد مجاز است"
                if self.min_height and height < self.min_height:
                    return False, "ارتفاع تصویر کمتر از حد مجاز است"
                if self.max_height and height > self.max_height:
                    return False, "ارتفاع تصویر بیشتر از حد مجاز است"
                
                # بررسی DPI
                if self.min_dpi:
                    dpi = img.info.get('dpi', (72, 72))[0]
                    if dpi < self.min_dpi:
                        return False, f"DPI تصویر ({dpi}) کمتر از حد مجاز ({self.min_dpi}) است"
        
        except Exception as e:
            return False, f"خطا در بررسی تصویر: {str(e)}"
        
        return True, "طرح قابل پذیرش است"
