from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.orders.models import Order
from .models import Notification

@receiver(pre_save, sender=Order)
def store_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_status = sender.objects.get(pk=instance.pk).status
        except sender.DoesNotExist:
            old_status = None
        instance._previous_status = old_status
    else:
        instance._previous_status = None

@receiver(post_save, sender=Order)
def create_status_change_notification(sender, instance, created, **kwargs):
    prev_status = getattr(instance, '_previous_status', None)
    if created or (prev_status and instance.status != prev_status):
        Notification.objects.create(
            user=instance.customer,
            business=instance.business,
            type='order_status',
            title='تغییر وضعیت سفارش',
            content=f'سفارش شما به وضعیت {instance.get_status_display()} تغییر یافت.',
        )

