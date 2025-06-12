from django.utils import timezone
from jdatetime import datetime as jdatetime
from datetime import datetime
from django.core.exceptions import ValidationError
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def to_jalali(date):
    """تبدیل تاریخ میلادی به شمسی"""
    if not date:
        return ''
    try:
        # اگر date یک string است، آن را به datetime تبدیل کن
        if isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        jalali_date = jdatetime.fromgregorian(datetime=date)
        return jalali_date.strftime('%Y/%m/%d %H:%M')
    except Exception as e:
        logger.error(f"Error converting to Jalali: {str(e)}")
        return str(date)

def validate_file_size(file, max_size_mb=None):
    """اعتبارسنجی حجم فایل (به مگابایت)"""
    if max_size_mb is None:
        max_size_mb = get_system_setting('max_file_size_mb', 5)
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"حجم فایل نباید بیشتر از {max_size_mb} مگابایت باشد.")
    return file

def validate_file_format(file, allowed_formats=None):
    """اعتبارسنجی فرمت فایل"""
    if allowed_formats is None:
        allowed_formats = get_system_setting('allowed_file_formats', ['jpg', 'png', 'pdf', 'webm'])
    file_ext = file.name.split('.')[-1].lower()
    if file_ext not in allowed_formats:
        raise ValidationError(f"فرمت فایل باید یکی از {', '.join(allowed_formats)} باشد.")
    return file

def log_error(message, exception=None):
    """ثبت خطا با لاگ"""
    logger.error(f"{message}: {str(exception)}" if exception else message)

def get_system_setting(key, default=None):
    """دریافت تنظیمات سیستمی"""
    # این import اینجا انجام شده تا از وابستگی دایره‌ای جلوگیری شود
    from .models import SystemSetting
    try:
        setting = SystemSetting.objects.get(key=key)
        return setting.value
    except SystemSetting.DoesNotExist:
        return default

def get_default_settings():
    """تنظیمات پیش‌فرض سیستم"""
    return {
        'max_file_size_mb': 5,
        'allowed_file_formats': ['jpg', 'png', 'pdf', 'webm'],
        'default_currency': 'IRR',
        'items_per_page': 10,
    } 