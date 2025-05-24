from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from apps.business.models import Business
from apps.designs.models import Design
from apps.templates_app.models import UserTemplate
from apps.core.utils import log_error, to_jalali
from django.db.models import SET_NULL

User = get_user_model()

class Order(BaseModel):
    """مدل برای مدیریت سفارش‌های کاربران"""
    STATUS_CHOICES = (
        ('draft', _('پیش‌نویس')),
        ('pending', _('در انتظار تأیید')),
        ('confirmed', _('تأیید شده')),
        ('in_progress', _('در حال انجام')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
    )

    GARMENT_SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
        ('custom', _('سفارشی')),
    )
    
    FABRIC_TYPE_CHOICES = (
        ('cotton', _('پنبه')),
        ('polyester', _('پلی‌استر')),
        ('cotton_polyester', _('پنبه-پلی‌استر')),
        ('silk', _('ابریشم')),
        ('other', _('سایر')),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name=_("مشتری"), null=True, blank=True)
    business = models.ForeignKey('business.Business', on_delete=models.CASCADE, related_name='orders', verbose_name=_("کسب‌وکار"), null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("وضعیت"))
    
    garment_size = models.CharField(max_length=20, choices=GARMENT_SIZE_CHOICES, verbose_name=_("سایز لباس"), null=True, blank=True)
    custom_size_details = models.JSONField(null=True, blank=True, verbose_name=_("جزئیات سایز سفارشی"))
    fabric_type = models.CharField(max_length=20, choices=FABRIC_TYPE_CHOICES, verbose_name=_("نوع پارچه"), null=True, blank=True)
    fabric_color = models.CharField(max_length=50, verbose_name=_("رنگ پارچه"), null=True, blank=True)
    fabric_weight = models.PositiveIntegerField(help_text=_("گرم بر متر مربع"), verbose_name=_("وزن پارچه"), null=True, blank=True)
    fabric_details = models.TextField(blank=True, verbose_name=_("توضیحات اضافی پارچه"))
    
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("قیمت کل (ریال)"), null=True, blank=True)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name=_("مبلغ پیش‌پرداخت (ریال)"))
    is_paid = models.BooleanField(default=False, verbose_name=_("پرداخت شده"))
    
    delivery_date = models.DateField(verbose_name=_("تاریخ تحویل"), null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تکمیل"))
    
    customer_notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های مشتری"))
    internal_notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های داخلی"))
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های عمومی"))

    def calculate_total_price(self):
        """محاسبه قیمت کل سفارش"""
        total = 0
        for item in self.items.all():
            total += item.quantity * item.unit_price
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

    class Meta:
        verbose_name = _("سفارش")
        verbose_name_plural = _("سفارش‌ها")
        ordering = ['-created_at']

class OrderItem(BaseModel):
    """مدل برای مدیریت آیتم‌های سفارش"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=_("سفارش"))
    design = models.ForeignKey(Design, on_delete=models.PROTECT, related_name='order_items', verbose_name=_("طرح"), null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name=_("تعداد"), null=True, blank=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name=_("قیمت واحد (ریال)"), null=True, blank=True)
    
    print_location = models.ForeignKey('print_locations.PrintLocation', on_delete=models.PROTECT, verbose_name=_("محل چاپ"), null=True, blank=True)
    print_dimensions = models.CharField(max_length=100, verbose_name=_("ابعاد چاپ"), null=True, blank=True)
    color_count = models.PositiveIntegerField(default=1, verbose_name=_("تعداد رنگ"))
    
    notes = models.TextField(blank=True, verbose_name=_("توضیحات"))
    
    @property
    def jalali_created_at(self):
        """تبدیل تاریخ ایجاد به شمسی"""
        return to_jalali(self.created_at)

    def save(self, *args, **kwargs):
        # محاسبه خودکار قیمت بر اساس آیتم انتخاب شده
        if self.design and not self.unit_price:
            self.unit_price = self.design.price if hasattr(self.design, 'price') else 0
            
        # محاسبه قیمت کل بر اساس تعداد
        single_price = self.unit_price / self.quantity if self.quantity > 0 and self.unit_price else 0
        self.unit_price = single_price * self.quantity
        
        try:
            super().save(*args, **kwargs)
            # بروزرسانی قیمت کل سفارش
            if self.order:
                self.order.calculate_total_price()
        except Exception as e:
            log_error(f"Error saving order item for order {self.order.id}", e)
            raise

    def __str__(self):
        item_name = self.design.title if self.design else 'بدون آیتم'
        return f"{item_name} - سفارش {str(self.order.id)[:8]}"

    class Meta:
        verbose_name = _("آیتم سفارش")
        verbose_name_plural = _("آیتم‌های سفارش")
        ordering = ['order', 'id']
