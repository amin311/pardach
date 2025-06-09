from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model

class BaseModel(models.Model):
    """کلاس پایه برای استفاده در همه مدل‌های دیگر"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("شناسه"))
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True, verbose_name=_("آخرین بروزرسانی"))

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.__class__.__name__} ({str(self.id)})"

class ThumbnailMixin(models.Model):
    """میکسین برای بهینه‌سازی خودکار تصاویر بندانگشتی"""
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True, verbose_name=_("تصویر بندانگشتی"))

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.thumbnail:
            try:
                image = Image.open(self.thumbnail)
                if image.size[0] > 300:
                    image.thumbnail((300, 300))
                    output = BytesIO()
                    image.save(output, format='JPEG', quality=85)
                    output.seek(0)
                    self.thumbnail = InMemoryUploadedFile(
                        output, 'ImageField', f"{self.thumbnail.name.split('.')[0]}_thumb.jpg",
                        'image/jpeg', output.getbuffer().nbytes, None
                    )
            except Exception as e:
                from .utils import log_error
                log_error("Error optimizing thumbnail", e)
        super().save(*args, **kwargs)

class SystemSetting(models.Model):
    """مدل برای ذخیره و مدیریت تنظیمات سیستمی"""
    key = models.CharField(max_length=100, unique=True, verbose_name=_("کلید"))
    value = models.JSONField(verbose_name=_("مقدار"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))

    def __str__(self):
        return self.key

    class Meta:
        verbose_name = _("تنظیمات سیستم")
        verbose_name_plural = _("تنظیمات سیستم")

class SiteSetting(models.Model):
    """Key‑value store for global toggles such as `require_signup_for_home`."""
    key = models.CharField(max_length=50, unique=True)
    value = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Site setting"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.key

class HomeBlock(models.Model):
    """Configurable block rendered on the public Home page."""

    CATALOG_LINK = "catalog_link"
    ORDER_FORM = "order_form"
    BUSINESS_GRID = "business_grid"
    PROFILE_SHORTCUT = "profile_short"
    VIDEO_BANNER = "video_banner"

    BLOCK_TYPES = [
        (CATALOG_LINK, "Catalog Link"),
        (ORDER_FORM, "Order Form"),
        (BUSINESS_GRID, "Business Grid"),
        (PROFILE_SHORTCUT, "User Profile Shortcut"),
        (VIDEO_BANNER, "Video Banner"),
    ]

    title = models.CharField(max_length=60)
    type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    config = models.JSONField(blank=True, default=dict, help_text="Free‑form JSON required by the renderer on front‑end.")
    order = models.PositiveIntegerField(default=0, help_text="Display position; lower comes first.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("order",)
        verbose_name = "Home block"
        verbose_name_plural = "Home blocks"

    def __str__(self):
        return f"{self.order}. {self.title}"

class Tender(models.Model):
    """A public request opened by a customer so businesses can bid."""
    OPEN, AWARDED, CLOSED, CANCELLED = "OPEN", "AWARDED", "CLOSED", "CANCELLED"
    STATUS_CHOICES = [
        (OPEN, "Open"),
        (AWARDED, "Awarded"),
        (CLOSED, "Closed"),
        (CANCELLED, "Cancelled"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    customer = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name="tenders")
    deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"#{self.id} – {self.title}"

class Business(models.Model):
    """Simplified placeholder; your existing Business model likely richer."""
    name = models.CharField(max_length=120)
    owner = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    # … other fields …
    def __str__(self):
        return self.name

class Bid(models.Model):
    """Offer placed by a Business for a Tender."""
    PENDING, ACCEPTED, REJECTED = "PENDING", "ACCEPTED", "REJECTED"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
    ]

    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="bids")
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tender", "business")
        ordering = ("amount",)

    def __str__(self):
        return f"Bid {self.amount} by {self.business} on tender {self.tender_id}"

class Workshop(models.Model):
    """Production workshop with daily capacity (e.g., pieces per day)."""
    name = models.CharField(max_length=120)
    manager = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True, blank=True)
    daily_capacity = models.PositiveIntegerField(default=0)
    used_capacity = models.PositiveIntegerField(default=0)  # auto‑calc
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def adjust_capacity(self, delta: int):
        self.used_capacity = max(0, self.used_capacity + delta)
        self.save(update_fields=["used_capacity"])

class WorkshopTask(models.Model):
    TODO, IN_PROGRESS, DONE = "TODO", "IN_PROGRESS", "DONE"
    STATUS_CHOICES = [
        (TODO, "Todo"),
        (IN_PROGRESS, "In progress"),
        (DONE, "Done"),
    ]
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="tasks")
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=TODO)
    quantity = models.PositiveIntegerField(default=1)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("status", "due_date")

    def __str__(self):
        return f"Task {self.id} ({self.status})"

class WorkshopReport(models.Model):
    """Progress report for a workshop task."""
    task = models.ForeignKey(WorkshopTask, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey('authentication.User', on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    progress = models.PositiveIntegerField(default=0)  # 0‑100
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.progress}% for task {self.task_id}"

class Award(models.Model):
    tender = models.OneToOneField(Tender, on_delete=models.CASCADE, related_name="award")
    bid = models.OneToOneField(Bid, on_delete=models.CASCADE, related_name="award")
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Award for tender {self.tender_id} to bid {self.bid_id}"

class Order(models.Model):
    NEW, IN_PROGRESS, COMPLETED, CANCELLED = "NEW", "IN_PROGRESS", "COMPLETED", "CANCELLED"
    STATUS_CHOICES = [
        (NEW, "New"),
        (IN_PROGRESS, "In progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]
    tender = models.ForeignKey(Tender, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    customer = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name="core_orders")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} – {self.status}"

class OrderStage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=60)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    sequence = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sequence",)

    def __str__(self):
        return f"Stage {self.sequence} of Order {self.order_id}"

    @property
    def is_paid(self):
        return self.amount_paid >= self.amount_due

class Transaction(models.Model):
    INITIATED, SUCCESS, FAIL = "INITIATED", "SUCCESS", "FAIL"
    STATUS_CHOICES = [
        (INITIATED, "Initiated"),
        (SUCCESS, "Success"),
        (FAIL, "Failed"),
    ]
    order_stage = models.ForeignKey(OrderStage, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    provider = models.CharField(max_length=30, default="manual")  # e.g., zarinpal, stripe
    external_id = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=INITIATED)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Txn {self.id} – {self.status}"

class SetDesign(models.Model):
    SUBMITTED, APPROVED, REJECTED = "SUBMITTED", "APPROVED", "REJECTED"
    STATUS = [
        (SUBMITTED, "Submitted"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected")
    ]
    order_stage = models.ForeignKey(OrderStage, on_delete=models.CASCADE, related_name="designs")
    designer = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name="setdesigns")
    design_file = models.FileField(upload_to="designs/", verbose_name=_("فایل طراحی"))
    preview = models.ImageField(upload_to="design_previews/", null=True, blank=True, verbose_name=_("پیش‌نمایش"))
    status = models.CharField(max_length=10, choices=STATUS, default=SUBMITTED, verbose_name=_("وضعیت"))
    description = models.TextField(blank=True, verbose_name=_("توضیحات"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("تاریخ ایجاد"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("تاریخ به‌روزرسانی"))

    class Meta:
        verbose_name = _("طراحی ست")
        verbose_name_plural = _("طراحی‌های ست")
        ordering = ["-created_at"]

    def __str__(self):
        return f"طراحی {self.id} برای مرحله {self.order_stage_id}"

    def save(self, *args, **kwargs):
        if self.design_file and not self.preview:
            try:
                # تبدیل فایل طراحی به پیش‌نمایش
                image = Image.open(self.design_file)
                image.thumbnail((800, 800))
                output = BytesIO()
                image.save(output, format='JPEG', quality=85)
                output.seek(0)
                self.preview = InMemoryUploadedFile(
                    output, 'ImageField',
                    f"{self.design_file.name.split('.')[0]}_preview.jpg",
                    'image/jpeg',
                    output.getbuffer().nbytes,
                    None
                )
            except Exception as e:
                from .utils import log_error
                log_error("Error creating design preview", e)
        super().save(*args, **kwargs)
