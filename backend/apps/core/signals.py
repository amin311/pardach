from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import (
    Bid, Tender, Award, Workshop, WorkshopTask, WorkshopReport,
    Order, OrderStage, Transaction, SetDesign
)

@receiver(post_save, sender=Bid)
def auto_award_and_notify(sender, instance: Bid, created, **kwargs):
    """If customer accepts a bid (status→ACCEPTED) create Award & notify parties."""
    if not created and instance.status == Bid.ACCEPTED:
        # Create award only once
        Award.objects.get_or_create(tender=instance.tender, defaults={"bid": instance})
        instance.tender.status = Tender.AWARDED
        instance.tender.save(update_fields=["status"])

        # OPTIONAL: create a WorkshopTask if you have such model
        # from workshop.models import WorkshopTask
        # task = WorkshopTask.objects.create(
        #     tender=instance.tender,
        #     business=instance.business,
        #     ...
        # )
        # instance.award.workshop_task = task
        # instance.award.save()

        # Notify (pseudo‑code, adapt to your Notification model)
        # Notification.objects.create(user=instance.tender.customer,
        #     message=f"Bid {instance.id} has been awarded.") 

@receiver(pre_save, sender=WorkshopTask)
def check_workshop_capacity(sender, instance, **kwargs):
    if instance.workshop.used_capacity + instance.quantity > instance.workshop.daily_capacity:
        raise ValueError("ظرفیت کارگاه کافی نیست")

@receiver(post_save, sender=WorkshopTask)
def update_workshop_capacity(sender, instance, created, **kwargs):
    if created:
        instance.workshop.used_capacity += instance.quantity
        instance.workshop.save()

@receiver(post_save, sender=WorkshopReport)
def update_task_progress(sender, instance, created, **kwargs):
    if created:
        task = instance.task
        task.progress = instance.progress
        if instance.progress >= 100:
            task.status = "completed"
        task.save()

@receiver(post_save, sender=Transaction)
def update_order_stage_payment(sender, instance, created, **kwargs):
    if created and instance.status == Transaction.SUCCESS:
        order_stage = instance.order_stage
        order_stage.amount_paid += instance.amount
        if order_stage.is_paid:
            order_stage.paid_at = instance.created_at
        order_stage.save()

@receiver(post_save, sender=OrderStage)
def update_order_status(sender, instance, created, **kwargs):
    if not created:
        order = instance.order
        all_stages = order.stages.all()
        if all(stage.is_paid for stage in all_stages):
            order.status = Order.COMPLETED
            order.save(update_fields=["status"])

@receiver(post_save, sender=SetDesign)
def notify_order_stage(sender, instance, created, **kwargs):
    """اطلاع‌رسانی به مرحله سفارش در صورت تغییر وضعیت طراحی"""
    if not created and instance.status in [SetDesign.APPROVED, SetDesign.REJECTED]:
        order_stage = instance.order_stage
        # اینجا می‌توانید اعلان‌ها را اضافه کنید
        # Notification.objects.create(
        #     user=order_stage.order.customer,
        #     message=f"طراحی {instance.id} {instance.get_status_display()} شد"
        # ) 