from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SetDesign
from apps.notification.utils import push_notification

@receiver(post_save, sender=SetDesign)
def handle_setdesign_update(sender, instance, created, **kwargs):
    if created and instance.status == "in_progress":
        # اعلان برای ست‌بند
        push_notification(
            user=instance.designer,
            title="کار ست‌بندی جدید",
            body=f"ست‌بندی سفارش #{instance.order_item.order.id} به شما واگذار شد."
        )
    elif instance.status == "pending_approval":
        # اعلان برای مشتری/چاپخانه
        push_notification(
            user=instance.order_item.order.user,
            title="ست‌بندی آماده تأیید است",
            body=f"نسخه {instance.version} ست‌بندی سفارش شما آماده است."
        )
    elif instance.status == "completed":
        # سفارش می‌تواند وارد مرحله چاپ شود
        order = instance.order_item.order
        order.status = "ready_for_print"
        order.save(update_fields=["status"]) 