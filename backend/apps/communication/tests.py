from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Chat, Message, Notification
import pytest

User = get_user_model()

class CommunicationModelTests(TestCase):
    """تست‌های مدل‌های اپ communication"""
    
    def setUp(self):
        """راه‌اندازی داده‌های تست"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
    
    def test_chat_creation(self):
        """تست ایجاد چت"""
        chat = Chat.objects.create(title='چت تست')
        chat.participants.add(self.user1, self.user2)
        
        self.assertEqual(chat.title, 'چت تست')
        self.assertEqual(chat.participants.count(), 2)
        self.assertIn(self.user1, chat.participants.all())
        self.assertIn(self.user2, chat.participants.all())
    
    def test_message_creation(self):
        """تست ایجاد پیام"""
        chat = Chat.objects.create(title='چت تست')
        chat.participants.add(self.user1, self.user2)
        
        message = Message.objects.create(
            chat=chat,
            sender=self.user1,
            content='سلام دنیا!'
        )
        
        self.assertEqual(message.content, 'سلام دنیا!')
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.chat, chat)
        self.assertFalse(message.is_read)
    
    def test_notification_creation(self):
        """تست ایجاد اعلان"""
        notification = Notification.objects.create(
            user=self.user1,
            type='general',
            title='اعلان تست',
            content='این یک اعلان تست است',
            link='/test'
        )
        
        self.assertEqual(notification.title, 'اعلان تست')
        self.assertEqual(notification.content, 'این یک اعلان تست است')
        self.assertEqual(notification.user, self.user1)
        self.assertEqual(notification.type, 'general')
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.link, '/test')

class CommunicationAPITests(TestCase):
    """تست‌های API اپ communication"""
    
    def setUp(self):
        """راه‌اندازی داده‌های تست"""
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.user1)
    
    def test_chat_list_api(self):
        """تست API لیست چت‌ها"""
        # ایجاد چند چت
        chat1 = Chat.objects.create(title='چت اول')
        chat1.participants.add(self.user1, self.user2)
        
        chat2 = Chat.objects.create(title='چت دوم')
        chat2.participants.add(self.user1)
        
        # درخواست به API
        response = self.client.get('/api/communication/chats/')
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'چت دوم')  # بر اساس ترتیب نزولی تاریخ ایجاد
        self.assertEqual(response.data[1]['title'], 'چت اول')
    
    def test_create_chat_api(self):
        """تست API ایجاد چت"""
        # داده‌های چت جدید
        data = {
            'title': 'چت جدید',
            'participant_ids': [self.user2.id]
        }
        
        # درخواست به API
        response = self.client.post('/api/communication/chats/', data, format='json')
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'چت جدید')
        
        # بررسی ایجاد چت در پایگاه داده
        self.assertTrue(Chat.objects.filter(title='چت جدید').exists())
        chat = Chat.objects.get(title='چت جدید')
        self.assertEqual(chat.participants.count(), 2)  # شامل کاربر جاری و کاربر دوم
    
    def test_send_message_api(self):
        """تست API ارسال پیام"""
        # ایجاد چت
        chat = Chat.objects.create(title='چت تست')
        chat.participants.add(self.user1, self.user2)
        
        # داده‌های پیام جدید
        data = {
            'content': 'سلام دنیا!'
        }
        
        # درخواست به API
        response = self.client.post(f'/api/communication/chats/{chat.id}/messages/', data, format='json')
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], 'سلام دنیا!')
        
        # بررسی ایجاد پیام در پایگاه داده
        self.assertTrue(Message.objects.filter(content='سلام دنیا!').exists())
        message = Message.objects.get(content='سلام دنیا!')
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.chat, chat)
    
    def test_notification_list_api(self):
        """تست API لیست اعلانات"""
        # ایجاد چند اعلان
        Notification.objects.create(
            user=self.user1,
            type='general',
            title='اعلان اول',
            content='محتوای اعلان اول'
        )
        
        Notification.objects.create(
            user=self.user1,
            type='order_status',
            title='اعلان دوم',
            content='محتوای اعلان دوم'
        )
        
        # درخواست به API
        response = self.client.get('/api/communication/notifications/')
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        
        # تست فیلتر بر اساس نوع
        response = self.client.get('/api/communication/notifications/?type=general')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'اعلان اول')
    
    def test_mark_notification_read_api(self):
        """تست API علامت‌گذاری اعلان به‌عنوان خوانده‌شده"""
        # ایجاد اعلان
        notification = Notification.objects.create(
            user=self.user1,
            type='general',
            title='اعلان تست',
            content='محتوای اعلان'
        )
        
        # بررسی وضعیت اولیه
        self.assertFalse(notification.is_read)
        
        # درخواست به API
        response = self.client.post(f'/api/communication/notifications/{notification.id}/read/')
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_read'])
        
        # بررسی تغییر در پایگاه داده
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
