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
    """مدل خانواده‌های طرح"""
    name = models.CharField(max_length=255, unique=True, verbose_name=_("نام خانواده"))
    slug = models.SlugField(max_length=280, unique=True, blank=True, null=True, verbose_name=_("اسلاگ"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    
    # ارتباطات
    tags = models.ManyToManyField(Tag, blank=True, related_name='families', verbose_name=_("برچسب‌ها"))
    categories = models.ManyToManyField(DesignCategory, blank=True, related_name='families', verbose_name=_("دسته‌بندی‌ها"))
    
    # نیازمندی‌های طرح
    required_design_types = models.JSONField(
        default=dict,
        verbose_name=_("نیازمندی‌های طرح"),
        help_text=_("نوع و تعداد طرح‌های مورد نیاز برای این خانواده")
    )
    exclusive_design_types = models.JSONField(
        default=list,
        verbose_name=_("انواع طرح‌های انحصاری"),
        help_text=_("انواع طرح‌هایی که فقط مختص این خانواده هستند")
    )
    
    # وضعیت
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("آخرین بروزرسانی"))

    def __str__(self):
        return self.name

    @property
    def designs_count(self):
        return self.designs.count()

    def can_include_design(self, design):
        """بررسی امکان استفاده از طرح در این خانواده"""
        # بررسی نوع طرح
        if design.design_type in self.exclusive_design_types:
            return True
            
        # بررسی نیازمندی‌ها
        required_count = self.required_design_types.get(design.design_type, 0)
        current_count = self.designs.filter(design_type=design.design_type).count()
        
        return current_count < required_count

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

    TYPE_CHOICES = (
        ('vector', _('وکتوری')),
        ('image', _('عکس')),
        ('combined', _('ترکیبی')),
    )

    DESIGN_TYPE_CHOICES = (
        ('flower', _('گل')),
        ('pattern', _('نقش')),
        ('text', _('متن')),
        ('logo', _('لوگو')),
        ('other', _('سایر')),
    )

    title = models.CharField(max_length=255, verbose_name=_("عنوان طرح"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    designer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs', verbose_name=_("طراح"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='created_designs', verbose_name=_("ایجاد کننده"))
    
    # فیلد تعیین نوع طرح (وکتور، عکس یا ترکیبی)
    design_type = models.CharField(max_length=20, choices=TYPE_CHOICES,
                                   default='vector', verbose_name=_("نوع طرح"))
    
    # فیلد فایل وکتور (برای طرح‌های وکتوری)
    vector_file = models.FileField(
        upload_to='designs/files/',
        validators=[FileExtensionValidator(allowed_extensions=['svg', 'ai', 'eps', 'pdf'])],
        verbose_name=_("فایل وکتور"),
        blank=True, null=True
    )
    # فیلد تصویر محصول (برای طرح‌های عکسی یا پیش‌نمایش)
    image_file = models.ImageField(
        upload_to='designs/images/',
        verbose_name=_("تصویر محصول"),
        blank=True, null=True
    )
    # فیلد فایل مخصوص دستگاه لیزر
    laser_file = models.FileField(
        upload_to='designs/laser/',
        verbose_name=_("فایل مخصوص لیزر"),
        blank=True, null=True
    )
    
    # ابعاد و اندازه
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("عرض (پیکسل)"))
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("ارتفاع (پیکسل)"))
    
    # ارتباطات
    categories = models.ManyToManyField('DesignCategory', related_name='designs', verbose_name=_("دسته‌بندی‌ها"))
    tags = models.ManyToManyField('Tag', related_name='designs', verbose_name=_("برچسب‌ها"))
    similar_designs = models.ManyToManyField('self', blank=True, symmetrical=False,
                                           related_name='related_designs',
                                           verbose_name=_("طرح‌های مشابه"))
    
    # وضعیت و آمار
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("وضعیت"))
    is_public = models.BooleanField(default=False, verbose_name=_("عمومی"))
    price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("قیمت (ریال)"))
    views_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد بازدید"))
    downloads_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد دانلود"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("طرح")
        verbose_name_plural = _("طرح‌ها")
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # بهینه‌سازی خودکار تصاویر
        if self.image_file:
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files import File

                img = Image.open(self.image_file)
                if img.size[0] > 800:
                    img.thumbnail((800, 800))
                    img_io = BytesIO()
                    img.save(img_io, 'JPEG', quality=85)
                    img_io.seek(0)
                    self.image_file = File(img_io, name=self.image_file.name)
            except Exception as e:
                from apps.core.utils import log_error
                log_error("Error optimizing image", e)
        super().save(*args, **kwargs)

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

class PrintLocation(BaseModel):
    """مدل محل‌های چاپ روی لباس (آستین، پشت، جیب و...)"""
    LOCATION_CHOICES = [
        ('front', _('جلو')),
        ('back', _('پشت')),
        ('sleeve_left', _('آستین چپ')),
        ('sleeve_right', _('آستین راست')),
        ('pocket', _('جیب')),
        ('collar', _('یقه')),
        ('rakab', _('رکب')),
        ('cuff', _('سر آستین')),
        ('hem', _('دامن')),
    ]
    
    code = models.CharField(max_length=32, unique=True, verbose_name=_("کد محل"))
    name = models.CharField(max_length=100, verbose_name=_("نام محل روی لباس"))
    location_type = models.CharField(max_length=20, choices=LOCATION_CHOICES, verbose_name=_("نوع محل"))
    price_modifier = models.DecimalField(
        max_digits=7, 
        decimal_places=2, 
        default=0,
        verbose_name=_("ضریب قیمت")
    )
    max_width_cm = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, blank=True,
        verbose_name=_("حداکثر عرض (سانتی‌متر)")
    )
    max_height_cm = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, blank=True,
        verbose_name=_("حداکثر ارتفاع (سانتی‌متر)")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    class Meta:
        verbose_name = _("محل چاپ")
        verbose_name_plural = _("محل‌های چاپ")
        ordering = ['location_type', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"

    def calculate_print_cost(self, base_price, design_complexity=1):
        """محاسبه هزینه چاپ بر اساس ضریب محل"""
        return base_price * float(self.price_modifier) * design_complexity

class Template(BaseModel):
    """مدل قالب‌های لباس"""
    name = models.CharField(max_length=255, verbose_name=_("نام قالب"))
    slug = models.SlugField(max_length=280, unique=True, blank=True, null=True, verbose_name=_("اسلاگ"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    
    # تصاویر
    preview_image = models.ImageField(upload_to='templates/previews/', verbose_name=_("تصویر پیش‌نمایش"))
    thumbnail = models.ImageField(upload_to='templates/thumbnails/', verbose_name=_("تصویر بندانگشتی"))
    
    # قیمت‌ها
    base_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت پایه (ریال)"))
    
    # ارتباطات
    categories = models.ManyToManyField(DesignCategory, related_name='design_templates', verbose_name=_("دسته‌بندی‌ها"))
    tags = models.ManyToManyField(Tag, related_name='design_templates', verbose_name=_("برچسب‌ها"))
    print_locations = models.ManyToManyField(PrintLocation, related_name='design_templates', verbose_name=_("محل‌های چاپ"))
    
    # وضعیت
    is_active = models.BooleanField(default=True, verbose_name=_("فعال"))
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("قالب")
        verbose_name_plural = _("قالب‌ها")
        ordering = ['-created_at']

class PhysicalStamp(BaseModel):
    """مدل مهرهای فیزیکی"""
    STATUS_CHOICES = (
        ('available', _('موجود')),
        ('in_use', _('در حال استفاده')),
        ('maintenance', _('در تعمیر')),
        ('retired', _('بازنشسته')),
    )

    name = models.CharField(max_length=255, verbose_name=_("نام مهر"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("کد مهر"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available', verbose_name=_("وضعیت"))
    size = models.CharField(max_length=100, verbose_name=_("اندازه"))
    material = models.CharField(max_length=100, verbose_name=_("جنس"))
    purchase_date = models.DateField(verbose_name=_("تاریخ خرید"), null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True, verbose_name=_("آخرین تعمیر"))
    next_maintenance = models.DateField(null=True, blank=True, verbose_name=_("تعمیر بعدی"))
    usage_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد استفاده"))
    max_usage = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("حداکثر تعداد استفاده"))
    location = models.CharField(max_length=255, verbose_name=_("محل نگهداری"))
    responsible_person = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='responsible_stamps', verbose_name=_("مسئول"))
    image = models.ImageField(upload_to='stamps/', blank=True, null=True, verbose_name=_("تصویر مهر"))
    laser_file = models.FileField(upload_to='stamps/laser/', blank=True, null=True, verbose_name=_("فایل لیزری"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = _("مهر فیزیکی")
        verbose_name_plural = _("مهرهای فیزیکی")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if self.usage_count >= self.max_usage if self.max_usage else False:
            self.status = 'retired'
        super().save(*args, **kwargs)

class StampRequest(BaseModel):
    """مدل درخواست حکاکی مهر"""
    STATUS_CHOICES = (
        ('pending', _('در انتظار')),
        ('approved', _('تأیید شده')),
        ('in_progress', _('در حال انجام')),
        ('completed', _('تکمیل شده')),
        ('rejected', _('رد شده')),
        ('cancelled', _('لغو شده')),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stamp_requests', verbose_name=_("مشتری"))
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='stamp_requests', verbose_name=_("کسب‌وکار"))
    design = models.ForeignKey(Design, on_delete=models.SET_NULL, null=True, related_name='stamp_requests', verbose_name=_("طرح"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    size = models.CharField(max_length=100, verbose_name=_("اندازه مهر"))
    material = models.CharField(max_length=100, verbose_name=_("جنس مهر"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("تعداد"))
    deadline = models.DateField(null=True, blank=True, verbose_name=_("مهلت تحویل"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت"))
    is_paid = models.BooleanField(default=False, verbose_name=_("پرداخت شده"))
    physical_stamp = models.ForeignKey(PhysicalStamp, on_delete=models.SET_NULL, null=True, blank=True, related_name='stamp_requests', verbose_name=_("مهر فیزیکی"))

    def __str__(self):
        return f"درخواست مهر {self.customer.get_full_name()} - {self.created_at}"

    class Meta:
        verbose_name = _("درخواست مهر")
        verbose_name_plural = _("درخواست‌های مهر")
        ordering = ['-created_at']
