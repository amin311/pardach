from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStage, OrderSection, OrderStatusHistory, OrderAssignment, PrintProcess
from apps.set_design.models import SetDesign
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Order)
def create_initial_order_stage(sender, instance, created, **kwargs):
    """ایجاد مرحله اولیه پس از ایجاد سفارش"""
    if created:
        OrderStage.objects.create(
            order=instance,
            stage_type='order_received',
            status='completed',
            started_at=instance.created_at,
            finished_at=instance.created_at,
            notes="سفارش دریافت و ثبت شد"
        )

@receiver(post_save, sender=Order)
def auto_assign_business(sender, instance, created, **kwargs):
    """تخصیص خودکار کسب‌وکار در صورت عدم تخصیص دستی"""
    if created and not instance.business:
        assigned = instance.auto_assign_business()
        if assigned:
            # ایجاد مرحله تخصیص
            OrderStage.objects.create(
                order=instance,
                stage_type='design_approval',
                status='pending',
                started_at=timezone.now(),
                notes="سفارش به کسب‌وکار تخصیص داده شد"
            )

@receiver(post_save, sender=Order)
def handle_status_change(sender, instance, **kwargs):
    """مدیریت تغییرات وضعیت سفارش"""
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # ایجاد یا به‌روزرسانی مرحله مربوطه
                stage_mapping = {
                    'confirmed': 'design_approval',
                    'set_design': 'set_design',
                    'printing': 'printing',
                    'completed': 'delivered',
                }
                
                stage_type = stage_mapping.get(instance.status)
                if stage_type:
                    stage, created = OrderStage.objects.get_or_create(
                        order=instance,
                        stage_type=stage_type,
                        defaults={
                            'status': 'in_progress' if instance.status != 'completed' else 'completed',
                            'started_at': timezone.now()
                        }
                    )
                    
                    if not created and instance.status == 'completed':
                        stage.status = 'completed'
                        stage.finished_at = timezone.now()
                        stage.save(update_fields=['status', 'finished_at'])
                        
                        # تنظیم زمان تکمیل سفارش
                        instance.completed_at = timezone.now()
                        instance.save(update_fields=['completed_at'])
        
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=OrderSection)
def create_set_design_for_section(sender, instance, created, **kwargs):
    """ایجاد ست‌بندی برای بخش‌های جدید در صورت نیاز"""
    if created and instance.order.status in ['confirmed', 'set_design']:
        # بررسی اینکه آیا طرح نیاز به ست‌بندی دارد
        if hasattr(instance.design, 'needs_set_design') and instance.design.needs_set_design:
            # تبدیل OrderSection به OrderItem موقت برای سازگاری
            from apps.orders.models import OrderItem
            
            # ایجاد OrderItem موقت برای این بخش
            order_item, created_item = OrderItem.objects.get_or_create(
                order=instance.order,
                design=instance.design,
                defaults={
                    'quantity': instance.quantity,
                    'unit_price': instance.calculate_cost()
                }
            )
            
            # ایجاد SetDesign
            SetDesign.objects.create(
                order_item=order_item,
                status='waiting',
                complexity_level=getattr(instance.design, 'complexity_level', 1),
                source_files=[str(instance.design.id)],
            )

@receiver(post_save, sender=SetDesign)
def handle_set_design_completion(sender, instance, **kwargs):
    """مدیریت تکمیل ست‌بندی"""
    if instance.status == 'completed':
        order = instance.order_item.order
        
        # بررسی تکمیل تمام ست‌بندی‌های سفارش
        all_set_designs = SetDesign.objects.filter(
            order_item__order=order
        )
        
        if all_set_designs.filter(status='completed').count() == all_set_designs.count():
            # تمام ست‌بندی‌ها تکمیل شده‌اند
            if order.status == 'set_design':
                order.status = 'printing_prep'
                order.save(update_fields=['status'])
                
                # ایجاد مرحله آماده‌سازی چاپ
                OrderStage.objects.create(
                    order=order,
                    stage_type='printing_prep',
                    status='in_progress',
                    started_at=timezone.now(),
                    notes="تمام ست‌بندی‌ها تکمیل شد، آماده چاپ"
                )

@receiver(pre_save, sender=Order)
def calculate_total_price_on_save(sender, instance, **kwargs):
    """محاسبه خودکار قیمت کل قبل از ذخیره"""
    if instance.pk:
        # محاسبه قیمت کل از بخش‌ها
        sections_total = sum(
            section.calculate_cost() 
            for section in instance.sections.all()
        )
        
        # محاسبه قیمت کل از آیتم‌ها
        items_total = sum(
            item.quantity * (item.unit_price or 0)
            for item in instance.items.all()
        )
        
        instance.total_price = sections_total + items_total

# سیگنال برای اطلاع‌رسانی تغییرات مهم
@receiver(post_save, sender=Order)
def send_order_notifications(sender, instance, created, **kwargs):
    """ارسال اطلاعیه‌های مربوط به سفارش"""
    try:
        from apps.notification.models import Notification
        
        if created:
            # اطلاعیه ایجاد سفارش به مشتری
            Notification.objects.create(
                user=instance.customer,
                title="ثبت سفارش جدید",
                message=f"سفارش شما با شماره {str(instance.id)[:8]} ثبت شد.",
                notification_type='order_created',
                data={'order_id': str(instance.id)}
            )
            
            # اطلاعیه به کسب‌وکار (در صورت وجود)
            if instance.business:
                for business_user in instance.business.users.filter(roles__name='business_manager'):
                    Notification.objects.create(
                        user=business_user.user,
                        title="سفارش جدید",
                        message=f"سفارش جدید با شماره {str(instance.id)[:8]} دریافت شد.",
                        notification_type='new_order_received',
                        data={'order_id': str(instance.id)}
                    )
    
    except ImportError:
        # مدل Notification وجود ندارد
        pass

@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    """ثبت تاریخچه تغییرات وضعیت سفارش"""
    if created:
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes="ایجاد سفارش جدید"
        )
    else:
        # بررسی تغییر وضعیت
        old_instance = Order.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            OrderStatusHistory.objects.create(
                order=instance,
                status=instance.status,
                notes=f"تغییر وضعیت از {old_instance.get_status_display()} به {instance.get_status_display()}"
            )

@receiver(post_save, sender=OrderAssignment)
def handle_order_assignment_status(sender, instance, created, **kwargs):
    """مدیریت تغییرات وضعیت تکلیف سفارش"""
    if not created:
        old_instance = OrderAssignment.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # بررسی تکمیل همه تکلیف‌ها
            if instance.status == 'completed':
                all_assignments = OrderAssignment.objects.filter(order=instance.order)
                all_completed = all_assignments.exclude(status='completed').exists()
                
                if not all_completed:
                    # به‌روزرسانی وضعیت سفارش
                    instance.order.status = 'completed'
                    instance.order.actual_delivery_date = timezone.now().date()
                    instance.order.save()

@receiver(post_save, sender=PrintProcess)
def handle_print_process_status(sender, instance, created, **kwargs):
    """مدیریت تغییرات وضعیت فرآیند چاپ"""
    if not created:
        old_instance = PrintProcess.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            if instance.status == 'completed':
                instance.completed_at = timezone.now()
                instance.save()
                
                # بررسی تکمیل همه فرآیندهای چاپ
                all_processes = PrintProcess.objects.filter(order_item=instance.order_item)
                all_completed = all_processes.exclude(status='completed').exists()
                
                if not all_completed:
                    # به‌روزرسانی وضعیت آیتم سفارش
                    instance.order_item.order_detail.order.status = 'in_progress'
                    instance.order_item.order_detail.order.save() 