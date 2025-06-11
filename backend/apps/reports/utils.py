from django.db.models import Sum, Count, Avg
from apps.orders.models import Order
from apps.payment.models import Payment
from django.utils import timezone
from datetime import timedelta, datetime
import pandas as pd
from apps.core.utils import to_jalali
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_sales_report(business=None, start_date=None, end_date=None):
    """
    تولید گزارش فروش براساس داده‌های سفارش‌ها
    
    business: کسب‌وکار مورد نظر (اختیاری)
    start_date: تاریخ شروع بازه
    end_date: تاریخ پایان بازه
    """
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)  # بازه پیش‌فرض: ۳۰ روز گذشته
    if not end_date:
        end_date = timezone.now()

    # دریافت سفارش‌های مرتبط با بازه زمانی
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    if business:
        orders = orders.filter(items__business=business).distinct()

    # اگر سفارشی وجود نداشت، داده‌های پیش‌فرض برگردان
    if not orders.exists():
        return {
            'labels': [to_jalali(start_date).split(' ')[0], to_jalali(end_date).split(' ')[0]],
            'values': [0, 0],
            'title': 'گزارش فروش',
            'type': 'bar'
        }

    # استفاده از pandas برای تحلیل داده‌ها
    df = pd.DataFrame(list(orders.values('created_at', 'total_price')))
    df['date'] = df['created_at'].apply(lambda x: to_jalali(x).split(' ')[0])
    
    # گروه‌بندی بر اساس تاریخ و محاسبه جمع فروش روزانه
    result = df.groupby('date').agg({'total_price': 'sum'}).reset_index()

    return {
        'labels': result['date'].tolist(),
        'values': result['total_price'].tolist(),
        'title': 'گزارش فروش',
        'type': 'bar'
    }

def generate_profit_report(business=None, start_date=None, end_date=None):
    """
    تولید گزارش سود براساس داده‌های پرداخت‌های موفق
    
    business: کسب‌وکار مورد نظر (اختیاری)
    start_date: تاریخ شروع بازه
    end_date: تاریخ پایان بازه
    """
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)  # بازه پیش‌فرض: ۳۰ روز گذشته
    if not end_date:
        end_date = timezone.now()

    # دریافت پرداخت‌های موفق مرتبط با بازه زمانی
    payments = Payment.objects.filter(created_at__range=[start_date, end_date], status='successful')
    if business:
        payments = payments.filter(order__items__business=business).distinct()

    # اگر پرداختی وجود نداشت، داده‌های پیش‌فرض برگردان
    if not payments.exists():
        return {
            'labels': [to_jalali(start_date).split(' ')[0], to_jalali(end_date).split(' ')[0]],
            'values': [0, 0],
            'title': 'گزارش سود',
            'type': 'line'
        }

    # استفاده از pandas برای تحلیل داده‌ها
    df = pd.DataFrame(list(payments.values('created_at', 'amount')))
    df['date'] = df['created_at'].apply(lambda x: to_jalali(x).split(' ')[0])
    
    # گروه‌بندی بر اساس تاریخ و محاسبه جمع پرداخت‌های روزانه
    result = df.groupby('date').agg({'amount': 'sum'}).reset_index()

    return {
        'labels': result['date'].tolist(),
        'values': result['amount'].tolist(),
        'title': 'گزارش سود',
        'type': 'line'
    }

def generate_user_activity_report(start_date=None, end_date=None):
    """
    تولید گزارش فعالیت کاربران براساس سفارش‌ها
    
    start_date: تاریخ شروع بازه
    end_date: تاریخ پایان بازه
    """
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)  # بازه پیش‌فرض: ۳۰ روز گذشته
    if not end_date:
        end_date = timezone.now()

    # دریافت سفارش‌های مرتبط با بازه زمانی
    orders = Order.objects.filter(created_at__range=[start_date, end_date])
    
    # اگر سفارشی وجود نداشت، داده‌های پیش‌فرض برگردان
    if not orders.exists():
        return {
            'labels': ['فعال', 'غیرفعال'],
            'values': [0, 0],
            'title': 'گزارش فعالیت کاربران',
            'type': 'pie'
        }

    # استخراج کاربران فعال (کاربرانی که سفارش ثبت کرده‌اند)
    active_users = orders.values('user').distinct().count()
    
    # استخراج تعداد کل کاربران
    total_users = User.objects.count()
    
    inactive_users = total_users - active_users

    return {
        'labels': ['کاربران فعال', 'کاربران غیرفعال'],
        'values': [active_users, inactive_users],
        'title': 'گزارش فعالیت کاربران',
        'type': 'pie'
    }

def generate_business_performance_report(business, start_date=None, end_date=None):
    """
    تولید گزارش عملکرد کسب‌وکار
    
    business: کسب‌وکار مورد نظر
    start_date: تاریخ شروع بازه
    end_date: تاریخ پایان بازه
    """
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)  # بازه پیش‌فرض: ۳۰ روز گذشته
    if not end_date:
        end_date = timezone.now()
        
    # آمار فروش (تعداد سفارش‌ها)
    orders_count = Order.objects.filter(
        created_at__range=[start_date, end_date],
        items__business=business
    ).distinct().count()
    
    # آمار مبلغ فروش
    sales_amount = Order.objects.filter(
        created_at__range=[start_date, end_date],
        items__business=business
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    # آمار پرداخت‌های موفق
    successful_payments = Payment.objects.filter(
        created_at__range=[start_date, end_date],
        status='successful',
        order__items__business=business
    ).distinct().count()
    
    # آمار پرداخت‌های ناموفق
    failed_payments = Payment.objects.filter(
        created_at__range=[start_date, end_date],
        status='failed',
        order__items__business=business
    ).distinct().count()
    
    return {
        'labels': ['تعداد سفارش‌ها', 'مبلغ فروش', 'پرداخت‌های موفق', 'پرداخت‌های ناموفق'],
        'values': [orders_count, sales_amount, successful_payments, failed_payments],
        'title': f'گزارش عملکرد کسب‌وکار {business.name}',
        'type': 'radar'
    } 