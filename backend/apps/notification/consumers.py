import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Notification
from django.contrib.auth import get_user_model
from apps.core.utils import to_jalali

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    """کانزیومر برای مدیریت اعلانات بلادرنگ از طریق WebSocket"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.notification_group_name = f'notifications_{self.user_id}'

        # اضافه کردن به گروه اعلانات کاربر
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )

        # پذیرش اتصال
        await self.accept()
        
        # ارسال اعلانات خوانده نشده هنگام اتصال
        unread_notifications = await self.get_unread_notifications(self.user_id)
        if unread_notifications:
            await self.send(text_data=json.dumps({
                'type': 'unread_notifications',
                'notifications': unread_notifications
            }))

    async def disconnect(self, close_code):
        # حذف از گروه اعلانات کاربر
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """دریافت پیام از کلاینت (مثلاً برای علامت‌گذاری اعلان)"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'mark_read':
            notification_id = data.get('notification_id')
            if notification_id:
                success = await self.mark_notification_read(notification_id, self.user_id)
                await self.send(text_data=json.dumps({
                    'type': 'mark_read_response',
                    'success': success,
                    'notification_id': notification_id
                }))

    # تابع برای ارسال اعلان جدید
    async def send_notification(self, event):
        """ارسال اعلان جدید به کلاینت"""
        notification = event['notification']
        
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification
        }))
    
    @database_sync_to_async
    def get_unread_notifications(self, user_id):
        """دریافت اعلانات خوانده نشده کاربر"""
        try:
            user = User.objects.get(id=user_id)
            notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')[:5]
            
            return [
                {
                    'id': str(notification.id),
                    'title': notification.title,
                    'content': notification.content,
                    'type': notification.type,
                    'link': notification.link,
                    'created_at': to_jalali(notification.created_at)
                }
                for notification in notifications
            ]
        except User.DoesNotExist:
            return []
        except Exception:
            return []
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id, user_id):
        """علامت‌گذاری اعلان به عنوان خوانده‌شده"""
        try:
            user = User.objects.get(id=user_id)
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.is_read = True
            notification.save()
            return True
        except (User.DoesNotExist, Notification.DoesNotExist):
            return False
        except Exception:
            return False 