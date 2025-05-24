"""
توابع کمکی برای اعلان‌رسانی
"""
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from django.utils.translation import gettext as _

def push_notification(user, title, body, data=None, notification_type="info"):
    """
    ارسال اعلان به کاربر از طریق WebSocket
    
    پارامترها:
    - user: کاربر هدف
    - title: عنوان اعلان
    - body: متن اعلان
    - data: داده‌های اضافی (اختیاری)
    - notification_type: نوع اعلان (info, success, warning, error)
    """
    if not user:
        return False
    
    channel_layer = get_channel_layer()
    
    try:
        # ارسال اعلان به کانال اختصاصی کاربر
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "notification",
                "message": {
                    "title": title,
                    "body": body,
                    "type": notification_type,
                    "data": data or {},
                    "timestamp": str(json.dumps({}, default=str))
                }
            }
        )
        
        # ذخیره اعلان در دیتابیس اگر مدل Notification وجود داشته باشد
        # (import در اینجا برای جلوگیری از چرخه واردات)
        from .models import Notification
        
        Notification.objects.create(
            user=user,
            title=title,
            message=body,
            notification_type=notification_type,
            data=data or {},
            is_read=False
        )
        
        return True
    except Exception as e:
        # در محیط توسعه خطا نمایش داده می‌شود
        print(f"Error sending notification: {str(e)}")
        return False 