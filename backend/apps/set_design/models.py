from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class SetDesign(BaseModel):
    """
    یک رکورد ست‌بندی برای دقیـقاً یک آیتم سفارش
    """
    order_item = models.ForeignKey(
        "orders.OrderItem",
        related_name="set_designs",
        on_delete=models.CASCADE,
        verbose_name=_("آیتم سفارش"),
    )
    designer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_setjobs",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={"roles__name": "set_designer"},
        verbose_name=_("ست‌بند"),
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="assigned_set_designs_active",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("مسئول ست‌بندی")
    )
    version = models.PositiveSmallIntegerField(default=1, verbose_name=_("نسخه"))
    parent = models.ForeignKey(
        "self",
        null=True, blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name=_("ست والد (برای نسخه‌بندی)"),
    )

    file = models.FileField(upload_to="sets/", verbose_name=_("فایل خروجی"))
    preview = models.ImageField(upload_to="sets/previews/", null=True, blank=True,
                               verbose_name=_("تصویر پیش‌نمایش"))
    source_files = models.JSONField(
        default=list, blank=True,
        verbose_name=_("فایل‌های منبع"),
        help_text=_("لیست فایل‌های اصلی طرح‌ها")
    )

    STATUS = (
        ("waiting",  _("در انتظار ست‌بند")),
        ("assigned", _("اختصاص داده شده")),
        ("in_progress", _("در حال ست‌بندی")),
        ("pending_approval", _("منتظر تأیید مشتری/چاپخانه")),
        ("revision_needed", _("نیاز به اصلاح")),
        ("approved", _("تأیید شده")),
        ("rejected", _("رد شده")),
        ("completed", _("تأیید و تکمیل")),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="waiting",
                             verbose_name=_("وضعیت"))
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0,
                               verbose_name=_("هزینه ست‌بندی (ریال)"))
    paid = models.BooleanField(default=False, verbose_name=_("پرداخت شده؟"))
    
    # فیلدهای جدید برای بهبود فرآیند
    auto_notification = models.BooleanField(default=True, verbose_name=_("اطلاع‌رسانی خودکار"))
    estimated_completion = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تخمینی تکمیل"))
    actual_completion = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان واقعی تکمیل"))
    complexity_level = models.PositiveSmallIntegerField(
        default=1, 
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_("سطح پیچیدگی")
    )
    revision_notes = models.TextField(blank=True, verbose_name=_("یادداشت‌های اصلاح"))

    class Meta:
        ordering = ("-created_at",)
        unique_together = ("order_item", "version")
        verbose_name = _("ست‌بندی")
        verbose_name_plural = _("ست‌بندی‌ها")

    def __str__(self):
        return f"Set #{self.order_item.id} v{self.version}"

    def save(self, *args, **kwargs):
        # ارسال اطلاعیه خودکار پس از تغییر وضعیت
        old_status = None
        if self.pk:
            old_status = SetDesign.objects.get(pk=self.pk).status
        
        super().save(*args, **kwargs)
        
        # ارسال اطلاعیه در صورت تغییر وضعیت
        if old_status and old_status != self.status and self.auto_notification:
            self.send_status_notification()

    def send_status_notification(self):
        """ارسال اطلاعیه تغییر وضعیت"""
        try:
            from apps.notification.models import Notification
            
            # تعیین گیرنده بر اساس وضعیت
            recipient = None
            title = ""
            message = ""
            
            if self.status == "assigned" and self.assigned_to:
                recipient = self.assigned_to
                title = "اختصاص ست‌بندی جدید"
                message = f"یک پروژه ست‌بندی جدید به شما اختصاص داده شد. شماره سفارش: {self.order_item.order.id}"
            
            elif self.status == "pending_approval" and self.order_item.order.customer:
                recipient = self.order_item.order.customer
                title = "ست‌بندی آماده بررسی"
                message = f"ست‌بندی سفارش شما آماده بررسی است. شماره سفارش: {self.order_item.order.id}"
            
            elif self.status == "completed" and self.order_item.order.customer:
                recipient = self.order_item.order.customer
                title = "تکمیل ست‌بندی"
                message = f"ست‌بندی سفارش شما تکمیل شد. شماره سفارش: {self.order_item.order.id}"
            
            if recipient:
                Notification.objects.create(
                    user=recipient,
                    title=title,
                    message=message,
                    notification_type='set_design_status_change',
                    data={'set_design_id': str(self.id), 'status': self.status}
                )
        except ImportError:
            # اگر مدل Notification وجود نداشت
            pass

    def assign_to_designer(self, designer):
        """اختصاص به طراح"""
        if self.status != 'waiting':
            raise ValueError("فقط ست‌بندی‌های در انتظار قابل اختصاص هستند")
        
        self.assigned_to = designer
        self.designer = designer  # برای سازگاری با کد قدیمی
        self.status = 'assigned'
        self.save(update_fields=['assigned_to', 'designer', 'status'])

    def mark_completed(self):
        """علامت‌گذاری به عنوان تکمیل شده"""
        if self.status != 'approved':
            raise ValueError("فقط ست‌بندی‌های تأیید شده قابل تکمیل هستند")
        
        self.status = 'completed'
        self.actual_completion = timezone.now()
        self.save(update_fields=['status', 'actual_completion'])
        
        # به‌روزرسانی وضعیت سفارش
        order = self.order_item.order
        if order.status == 'set_design':
            order.status = 'printing_prep'
            order.save(update_fields=['status'])

    # نسخه بعدی را بسازد
    def make_new_version(self, new_file, designer=None):
        return SetDesign.objects.create(
            order_item=self.order_item,
            version=self.version + 1,
            parent=self,
            file=new_file,
            designer=designer or self.designer,
            assigned_to=designer or self.assigned_to,
            status="in_progress",
            complexity_level=self.complexity_level,
        )

class SetDesignRequest(BaseModel):
    """مدل درخواست ست‌بندی طرح‌ها"""
    STATUS_CHOICES = (
        ('pending', _('در انتظار بررسی')),
        ('assigned', _('اختصاص داده شده')),
        ('in_progress', _('در حال انجام')),
        ('completed', _('تکمیل شده')),
        ('rejected', _('رد شده')),
        ('cancelled', _('لغو شده')),
    )
    
    PRIORITY_CHOICES = (
        (1, _('کم')),
        (2, _('متوسط')),
        (3, _('زیاد')),
        (4, _('فوری')),
    )
    
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='set_design_requests', verbose_name=_("سفارش"))
    designer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_set_design_requests', verbose_name=_("طراح"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("وضعیت"))
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name=_("اولویت"))
    
    requirements = models.TextField(verbose_name=_("نیازمندی‌ها"))
    reference_images = models.ManyToManyField(
        'designs.Design',
        related_name='reference_for_sets',
        blank=True,
        verbose_name=_("تصاویر مرجع")
    )
    
    deadline = models.DateTimeField(verbose_name=_("مهلت انجام"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("زمان تکمیل"))
    
    result_set = models.ForeignKey(
        'SetDesign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_request',
        verbose_name=_("ست نهایی")
    )
    
    notes = models.TextField(blank=True, verbose_name=_("یادداشت‌ها"))
    
    class Meta:
        verbose_name = _("درخواست ست‌بندی")
        verbose_name_plural = _("درخواست‌های ست‌بندی")
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"درخواست ست‌بندی برای سفارش {self.order.id}"

    def assign_to_designer(self, designer):
        """اختصاص درخواست به طراح"""
        if self.status != 'pending':
            raise ValueError("فقط درخواست‌های در انتظار قابل اختصاص هستند")
        
        self.designer = designer
        self.status = 'assigned'
        self.save(update_fields=['designer', 'status'])
        
        # ارسال اعلان به طراح
        from apps.notification.models import Notification
        Notification.objects.create(
            user=designer,
            title="درخواست ست‌بندی جدید",
            message=f"یک درخواست ست‌بندی جدید به شما اختصاص داده شد. شماره سفارش: {self.order.id}",
            notification_type='set_design_assigned'
        )

    def complete_request(self, set_design):
        """تکمیل درخواست و ثبت ست نهایی"""
        if self.status not in ['assigned', 'in_progress']:
            raise ValueError("وضعیت درخواست برای تکمیل معتبر نیست")
        
        self.result_set = set_design
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['result_set', 'status', 'completed_at'])
        
        # به‌روزرسانی وضعیت سفارش
        if self.order.status == 'pending':
            self.order.status = 'in_progress'
            self.order.save(update_fields=['status'])
        
        # ارسال اعلان به مشتری
        from apps.notification.models import Notification
        Notification.objects.create(
            user=self.order.customer,
            title="تکمیل ست‌بندی",
            message=f"ست‌بندی سفارش شما (شماره {self.order.id}) تکمیل شد.",
            notification_type='set_design_completed'
        ) 