from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from apps.authentication.models import User
from apps.business.models import Business
from apps.designs.models import Design
from django.core.validators import MinValueValidator

class Tender(BaseModel):
    """مدل مناقصه برای درخواست طراحی یا چاپ"""
    TENDER_TYPE_CHOICES = (
        ('design', _('طراحی')),
        ('print', _('چاپ')),
        ('both', _('طراحی و چاپ')),
    )
    
    STATUS_CHOICES = (
        ('draft', _('پیش‌نویس')),
        ('open', _('باز')),
        ('in_progress', _('در حال بررسی')),
        ('awarded', _('برنده‌دار شده')),
        ('cancelled', _('لغو شده')),
        ('completed', _('تکمیل شده')),
    )

    title = models.CharField(max_length=255, verbose_name=_("عنوان مناقصه"))
    description = models.TextField(verbose_name=_("توضیحات"))
    tender_type = models.CharField(max_length=20, choices=TENDER_TYPE_CHOICES, verbose_name=_("نوع مناقصه"))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tenders', verbose_name=_("ایجاد کننده"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name=_("وضعیت"))
    
    deadline = models.DateTimeField(verbose_name=_("مهلت ارسال پیشنهاد"))
    budget_min = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name=_("حداقل بودجه (ریال)"))
    budget_max = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name=_("حداکثر بودجه (ریال)"))
    
    required_design_count = models.PositiveIntegerField(default=1, verbose_name=_("تعداد طرح مورد نیاز"))
    required_print_count = models.PositiveIntegerField(default=0, verbose_name=_("تعداد چاپ مورد نیاز"))
    
    requirements = models.TextField(blank=True, verbose_name=_("الزامات فنی"))
    attachments = models.FileField(upload_to='tenders/attachments/', blank=True, null=True, verbose_name=_("فایل‌های پیوست"))
    
    winner = models.ForeignKey(Business, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_tenders', verbose_name=_("برنده مناقصه"))
    winning_bid = models.ForeignKey('TenderBid', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_tender', verbose_name=_("پیشنهاد برنده"))
    
    class Meta:
        verbose_name = _("مناقصه")
        verbose_name_plural = _("مناقصه‌ها")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_tender_type_display()})"

class TenderBid(BaseModel):
    """مدل پیشنهاد برای مناقصه"""
    STATUS_CHOICES = (
        ('submitted', _('ارسال شده')),
        ('under_review', _('در حال بررسی')),
        ('accepted', _('پذیرفته شده')),
        ('rejected', _('رد شده')),
    )

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name='bids', verbose_name=_("مناقصه"))
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='tender_bids', verbose_name=_("کسب‌وکار"))
    proposed_price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name=_("قیمت پیشنهادی (ریال)"))
    description = models.TextField(verbose_name=_("توضیحات پیشنهاد"))
    delivery_time = models.PositiveIntegerField(verbose_name=_("زمان تحویل (روز)"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted', verbose_name=_("وضعیت"))
    
    proposed_designs = models.ManyToManyField(Design, blank=True, related_name='tender_bids', verbose_name=_("طرح‌های پیشنهادی"))
    attachments = models.FileField(upload_to='tender_bids/attachments/', blank=True, null=True, verbose_name=_("فایل‌های پیوست"))
    
    class Meta:
        verbose_name = _("پیشنهاد مناقصه")
        verbose_name_plural = _("پیشنهادهای مناقصه")
        ordering = ['-created_at']
        unique_together = ['tender', 'business']  # هر کسب‌وکار فقط یک پیشنهاد برای هر مناقصه

    def __str__(self):
        return f"پیشنهاد {self.business.name} برای {self.tender.title}"
