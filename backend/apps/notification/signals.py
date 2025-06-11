from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.orders.models import Order
from .models import Notification

@receiver(pre_save, sender=Order)
def store_previous_status(sender, instance, **kwargs):
    """Store the current status before saving to detect changes."""
    if instance.pk:
        try:
            instance._previous_status = Order.objects.get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._previous_status = None

@receiver(post_save, sender=Order)
def order_status_notification(sender, instance, created, **kwargs):
    """Create a notification when an order status changes."""
    if created:
        return

    previous_status = getattr(instance, "_previous_status", None)
    if previous_status and previous_status != instance.status:
        Notification.objects.create(
            user=instance.customer,
            business=instance.business,
            type="order_status",
            title="به‌روزرسانی وضعیت سفارش",
            content=f"وضعیت سفارش شما به {instance.get_status_display()} تغییر یافت.",
        )
