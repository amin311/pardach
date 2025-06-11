from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from apps.business.models import Business
from apps.designs.models import Design, Template
from apps.templates_app.models import UserTemplate
from apps.core.utils import log_error, to_jalali
from django.db.models import SET_NULL
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.clothing.models import ClothingSection, RakebOrientation

User = get_user_model()

class OrderItem(models.Model):
    """آیتم‌های سفارش شامل طرح‌ها و محل‌های چاپ"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="items", null=True, blank=True)
    section = models.ForeignKey(ClothingSection, on_delete=models.PROTECT, related_name="order_items", verbose_name=_("بخش لباس"), null=True, blank=True)
    design = models.ForeignKey(Design, on_delete=models.PROTECT, related_name="order_items", verbose_name=_("طرح"), null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("تعداد"))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True, verbose_name=_("قیمت"))
    rakeb_orientation = models.CharField(max_length=7, choices=RakebOrientation.choices, default=RakebOrientation.OUTSIDE, verbose_name=_("رکب"))
    
    # فیلدهای اضافه شده مجدد
    color_count = models.PositiveIntegerField(default=1, verbose_name=_("تعداد رنگ"))
    print_dimensions = models.CharField(max_length=100, verbose_name=_("ابعاد چاپ"), null=True, blank=True)
    
    # قیمت‌ها
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت واحد (ریال)"))
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت کل (ریال)"))
    
    # یادداشت‌ها
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))
    
    # تاریخ‌ها
    created_at = models.DateTimeField(null=True, blank=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name=_("آخرین بروزرسانی"))

    @property
    def jalali_created_at(self):
        """تبدیل تاریخ ایجاد به شمسی"""
        return to_jalali(self.created_at) if self.created_at else None

    def save(self, *args, **kwargs):
        # محاسبه خودکار قیمت بر اساس آیتم انتخاب شده
        if self.design and not self.unit_price:
            self.unit_price = self.design.price if hasattr(self.design, 'price') else 0
            
        # محاسبه قیمت کل بر اساس تعداد
        if self.quantity and self.unit_price:
            self.total_price = self.unit_price * self.quantity
        elif self.order and self.unit_price:
            self.total_price = self.unit_price * self.quantity
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order.code} – {self.design.name} ({self.quantity})"

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")
        ordering = ['-created_at']

class Order(BaseModel):
    """مدل برای مدیریت سفارش‌های کاربران"""
    STATUS_CHOICES = (
        ('draft', _('پیش‌نویس')),
        ('pending', _('در انتظار تأیید')),
        ('confirmed', _('تأیید شده')),
        ('in_progress', _('در حال انجام')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
        ('returned', _('مرجوع شده')),
    )

    GARMENT_SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('3XL', '3XL'),
        ('custom', _('سفارشی')),
    )
    
    FABRIC_TYPE_CHOICES = (
        ('cotton', _('پنبه')),
        ('polyester', _('پلی‌استر')),
        ('cotton_polyester', _('پنبه-پلی‌استر')),
        ('lycra', _('لایکرا')),
        ('silk', _('ابریشم')),
        ('linen', _('کتان')),
    )

    PRINT_TYPE_CHOICES = (
        ('manual', _('دستی')),
        ('digital', _('دیجیتال')),
        ('screen', _('سیلک اسکرین')),
        ('embroidery', _('گلدوزی')),
        ('heat_transfer', _('پرس حرارتی')),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_("مشتری"))
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='orders', verbose_name=_("کسب‌وکار"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("وضعیت"))
    
    # اندازه لباس (عرض و ارتفاع)
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("عرض لباس (cm)"))
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("ارتفاع لباس (cm)"))
    garment_size = models.CharField(max_length=10, choices=GARMENT_SIZE_CHOICES, verbose_name=_("اندازه لباس"), null=True, blank=True)
    custom_size_details = models.JSONField(null=True, blank=True, verbose_name=_("جزئیات سایز سفارشی"))
    
    # نوع پارچه، رنگ و سایر مشخصات
    fabric_type = models.CharField(max_length=50, blank=True, verbose_name=_("نوع پارچه"))
    fabric_color = models.CharField(max_length=50, blank=True, verbose_name=_("رنگ پارچه"))
    fabric_material = models.CharField(max_length=50, blank=True, verbose_name=_("جنس پارچه"))
    fabric_weight = models.PositiveIntegerField(null=True, blank=True, help_text=_("گرم بر متر مربع"), verbose_name=_("وزن پارچه"))
    fabric_details = models.TextField(blank=True, verbose_name=_("توضیحات اضافی پارچه"))
    
    # گزینه‌های چاپ
    print_option = models.CharField(max_length=15, choices=PRINT_TYPE_CHOICES, default='manual', verbose_name=_("گزینه چاپ"))
    
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("قیمت کل (ریال)"), null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("مبلغ پیش‌پرداخت (ریال)"))
    is_paid = models.BooleanField(default=False, verbose_name=_("پرداخت شده"))
    
    delivery_date = models.DateField(null=True, blank=True, verbose_name=_("تاریخ تحویل"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تکمیل"))
    
    customer_notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های مشتری"))
    internal_notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های داخلی"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های عمومی"))

    def calculate_total_price(self):
        """محاسبه قیمت کل سفارش"""
        total = 0
        for section in self.sections.all():
            section_cost = section.calculate_cost()
            total += section_cost
        
        # اضافه کردن هزینه‌های اضافی
        for item in self.items.all():
            total += item.quantity * item.unit_price if item.unit_price else 0
            
        self.total_price = total
        self.save(update_fields=['total_price'])
        return total
        
    @property
    def jalali_created_at(self):
        """تبدیل تاریخ ایجاد به شمسی"""
        return to_jalali(self.created_at)
        
    @property
    def jalali_updated_at(self):
        """تبدیل تاریخ بروزرسانی به شمسی"""
        return to_jalali(self.updated_at)
        
    @property
    def items_count(self):
        """تعداد آیتم‌های سفارش"""
        return self.items.count()

    def __str__(self):
        return f"سفارش {self.id} - {self.customer.get_full_name() if self.customer else 'بدون مشتری'}"

    def save(self, *args, **kwargs):
        # تعیین خودکار کسب‌وکار چاپ با توجه به نقش کاربری ایجادکننده (اگر خالی باشد)
        if not self.business and hasattr(self, "_request_user"):
            from business.models import BusinessUser
            try:
                self.business = BusinessUser.objects.get(user=self._request_user).business
            except BusinessUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارش‌ها")
        ordering = ['-created_at']

class OrderSection(BaseModel):
    """مدل برای مدیریت بخش‌های انتخاب شده در سفارش"""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='sections', verbose_name=_("سفارش")
    )
    location = models.ForeignKey(
        'designs.PrintLocation', on_delete=models.PROTECT,
        related_name='order_sections', verbose_name=_("محل چاپ")
    )
    design = models.ForeignKey(
        'designs.Design', on_delete=models.PROTECT,
        related_name='order_sections', verbose_name=_("طرح")
    )
    is_inner_print = models.BooleanField(default=False, verbose_name=_("رکب به داخل"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("تعداد تکرار"))
    custom_width_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("عرض سفارشی (سانتی‌متر)")
    )
    custom_height_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("ارتفاع سفارشی (سانتی‌متر)")
    )
    special_instructions = models.TextField(blank=True, verbose_name=_("دستورات ویژه"))
    
    def calculate_cost(self):
        """محاسبه هزینه این بخش"""
        base_cost = self.design.price if hasattr(self.design, 'price') else 0
        location_cost = self.location.calculate_print_cost(base_cost)
        return location_cost * self.quantity

    def __str__(self):
        return f"{self.location.name} - {self.design.title} در سفارش {str(self.order.id)[:8]}"

    class Meta:
        verbose_name = _("بخش سفارش")
        verbose_name_plural = _("بخش‌های سفارش")
        unique_together = ('order', 'location', 'design')

class GarmentDetails(BaseModel):
    """مدل برای ذخیره ابعاد دقیق لباس"""
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE,
        related_name='garment_details', verbose_name=_("سفارش")
    )
    length_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("طول (سانتی‌متر)")
    )
    width_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("عرض (سانتی‌متر)")
    )
    sleeve_length_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("طول آستین (سانتی‌متر)")
    )
    chest_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("دور سینه (سانتی‌متر)")
    )
    shoulder_cm = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        verbose_name=_("عرض شانه (سانتی‌متر)")
    )
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های اندازه‌گیری"))

    def __str__(self):
        return f"ابعاد سفارش {str(self.order.id)[:8]}"

    class Meta:
        verbose_name = _("جزئیات لباس")
        verbose_name_plural = _("جزئیات لباس‌ها")

class OrderStage(BaseModel):
    """مدل برای پیگیری مراحل سفارش"""
    STAGE_CHOICES = [
        ('order_received', _('دریافت سفارش')),
        ('design_approval', _('تأیید طرح')),
        ('set_design', _('ست‌بندی')),
        ('printing_prep', _('آماده‌سازی چاپ')),
        ('printing', _('چاپ')),
        ('quality_check', _('کنترل کیفیت')),
        ('packaging', _('بسته‌بندی')),
        ('shipping', _('ارسال')),
        ('delivered', _('تحویل')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار')),
        ('in_progress', _('در جریان')),
        ('completed', _('تکمیل شده')),
        ('on_hold', _('متوقف')),
        ('cancelled', _('لغو شده')),
    ]

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='stages', verbose_name=_("سفارش")
    )
    stage_type = models.CharField(max_length=20, choices=STAGE_CHOICES, verbose_name=_("نوع مرحله"))
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان شروع"))
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان پایان"))
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_stages', verbose_name=_("مسئول")
    )
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))

    def __str__(self):
        return f"{self.get_stage_type_display()} - سفارش {str(self.order.id)[:8]}"

    class Meta:
        verbose_name = _("مرحله سفارش")
        verbose_name_plural = _("مراحل سفارش")
        ordering = ['order', 'stage_type']

class OrderDetail(models.Model):
    """جزئیات سفارش شامل مشخصات لباس و چاپ"""
    SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    )

    FABRIC_CHOICES = (
        ('cotton', _('پنبه')),
        ('polyester', _('پلی‌استر')),
        ('mixed', _('مختلط')),
    )

    PRINT_TYPE_CHOICES = (
        ('screen', _('چاپ سیلک')),
        ('digital', _('چاپ دیجیتال')),
        ('sublimation', _('چاپ سابلیمیشن')),
        ('embroidery', _('گلدوزی')),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='details', verbose_name=_("سفارش"))
    template = models.ForeignKey(Template, on_delete=models.PROTECT, related_name='order_details', verbose_name=_("قالب"))
    
    # مشخصات لباس
    size = models.CharField(max_length=5, choices=SIZE_CHOICES, verbose_name=_("سایز"))
    fabric = models.CharField(max_length=20, choices=FABRIC_CHOICES, verbose_name=_("نوع پارچه"))
    color = models.CharField(max_length=50, verbose_name=_("رنگ لباس"))
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("تعداد"))
    
    # مشخصات چاپ
    print_type = models.CharField(max_length=20, choices=PRINT_TYPE_CHOICES, verbose_name=_("نوع چاپ"))
    has_rakab = models.BooleanField(default=False, verbose_name=_("دارای رکب"))
    rakab_type = models.CharField(max_length=50, blank=True, verbose_name=_("نوع رکب"))
    
    # قیمت‌ها
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت واحد (ریال)"))
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت کل (ریال)"))
    
    # یادداشت‌ها
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.template.name} - {self.size} - {self.quantity} عدد"

    class Meta:
        verbose_name = _("جزئیات سفارش")
        verbose_name_plural = _("جزئیات سفارش‌ها")

class PrintProcess(models.Model):
    """مدل برای مدیریت مراحل چاپ سفارش"""
    STAGE_CHOICES = [
        ('design', _('طراحی')),
        ('prepress', _('پیش‌چاپ')),
        ('printing', _('چاپ')),
        ('postpress', _('پس‌چاپ')),
        ('quality_control', _('کنترل کیفیت')),
        ('packaging', _('بسته‌بندی')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('در انتظار')),
        ('in_progress', _('در حال انجام')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='print_processes', verbose_name=_("سفارش"), null=True, blank=True)
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default='design', verbose_name=_("مرحله"), null=True, blank=True)
    business_responsible = models.ForeignKey('business.Business', on_delete=models.SET_NULL, null=True, related_name='print_processes', verbose_name=_("مجری مسئول"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(default=timezone.now, verbose_name=_("تاریخ بروزرسانی"))

    class Meta:
        verbose_name = _("فرآیند چاپ")
        verbose_name_plural = _("فرآیندهای چاپ")
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.id:  # اگر رکورد جدید است
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        stage_display = self.get_stage_display() if self.stage else 'بدون مرحله'
        return f"{stage_display} - {self.order if self.order else 'بدون سفارش'}"

class OrderAssignment(models.Model):
    """تکلیف سفارش به کسب‌وکارها"""
    PROCESS_TYPE_CHOICES = (
        ('print', _('چاپ')),
        ('set', _('ست‌بندی')),
        ('delivery', _('تحویل')),
    )

    STATUS_CHOICES = (
        ('pending', _('در انتظار')),
        ('accepted', _('پذیرفته شده')),
        ('rejected', _('رد شده')),
        ('completed', _('تکمیل شده')),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='assignments', verbose_name=_("سفارش"))
    business = models.ForeignKey(Business, on_delete=models.PROTECT, related_name='order_assignments', verbose_name=_("کسب‌وکار"))
    process_type = models.CharField(max_length=20, choices=PROCESS_TYPE_CHOICES, verbose_name=_("نوع فرآیند"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    
    # قیمت‌ها
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("قیمت (ریال)"))
    
    # تاریخ‌ها
    deadline = models.DateTimeField(null=True, blank=True, verbose_name=_("مهلت انجام"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تکمیل"))
    
    # یادداشت‌ها
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))

    def __str__(self):
        return f"{self.get_process_type_display()} - {self.business.name}"

    class Meta:
        verbose_name = _("تکلیف سفارش")
        verbose_name_plural = _("تکلیف‌های سفارش")
        unique_together = ('order', 'business', 'process_type')

class OrderStatusHistory(models.Model):
    """تاریخچه تغییرات وضعیت سفارش"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history', verbose_name=_("سفارش"))
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, verbose_name=_("وضعیت"))
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='order_status_changes', verbose_name=_("تغییر دهنده"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ تغییر"))

    def __str__(self):
        return f"{self.order} - {self.get_status_display()}"

    class Meta:
        verbose_name = _("تاریخچه وضعیت سفارش")
        verbose_name_plural = _("تاریخچه وضعیت سفارش‌ها")
        ordering = ['-created_at']
