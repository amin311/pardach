from django.test import TestCase
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from datetime import datetime
from apps.orders.models import Order
from apps.payment.models import Payment
from apps.notification.models import Notification
from apps.designs.models import Design
from apps.business.models import Business
from apps.communication.models import Chat
from apps.core.models import SystemSetting
from apps.communication.models import ChatSession, ChatMessage

User = get_user_model()

@pytest.mark.django_db
class TestMainPageSummary:
    """تست‌های API خلاصه صفحه اصلی"""
    
    def setup_method(self):
        """راه‌اندازی داده‌های مورد نیاز برای تست"""
        # ایجاد کاربران
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='test123'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # ایجاد داده‌های نمونه
        business = Business.objects.create(
            name='تست کسب‌وکار',
            owner=self.user
        )
        
        Order.objects.create(
            user=self.user,
            total_price=10000,
            status='pending',
            created_at=datetime.now()
        )
        
        Payment.objects.create(
            user=self.user,
            amount=10000,
            status='successful',
            created_at=datetime.now()
        )
        
        Notification.objects.create(
            user=self.user,
            title='تست اعلان',
            message='این یک اعلان تست است',
            read=False,
            created_at=datetime.now()
        )
        
        Design.objects.create(
            title='طرح تست',
            image='test.jpg',
            created_by=self.user,
            created_at=datetime.now()
        )
        
        chat = Chat.objects.create(title='چت تست')
        chat.participants.add(self.user)
        
        # ایجاد API کلاینت
        self.client = APIClient()
    
    def test_main_page_summary_authenticated(self):
        """تست دریافت خلاصه صفحه اصلی برای کاربر احراز هویت شده"""
        self.client.force_authenticate(user=self.user)
        url = reverse('main:main_page_summary')
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert 'promotions' in response.data
        assert 'navigation' in response.data
        assert response.data['summary']['order_count'] == 1
        assert response.data['summary']['payment_count'] == 1
        assert response.data['summary']['unread_notifications'] == 1
        assert len(response.data['summary']['recent_orders']) == 1
        assert len(response.data['summary']['recent_designs']) == 1
    
    def test_main_page_summary_unauthenticated(self):
        """تست عدم دسترسی به خلاصه صفحه اصلی برای کاربر بدون احراز هویت"""
        url = reverse('main:main_page_summary')
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_main_page_summary_admin(self):
        """تست دریافت خلاصه صفحه اصلی برای کاربر ادمین"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('main:main_page_summary')
        
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # بررسی منوی ناوبری کامل برای ادمین
        visible_items = [item for item in response.data['navigation'] if item['visible']]
        assert len(visible_items) == 9  # تمام آیتم‌های منو برای ادمین نمایش داده می‌شوند

class MainSummaryViewTest(TestCase):
    def setUp(self):
        # ایجاد کاربران برای تست
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpassword', 
            is_staff=True,
            first_name='مدیر', 
            last_name='سیستم'
        )
        self.normal_user = User.objects.create_user(
            username='user', 
            email='user@example.com', 
            password='userpassword',
            first_name='کاربر', 
            last_name='عادی'
        )
        
        # ایجاد چند نمونه برای تست
        # ایجاد سفارش
        self.order = Order.objects.create(
            user=self.normal_user,
            status='pending',
            total_amount=150000,
            shipping_address='تهران، خیابان آزادی',
            tracking_code='ORD12345',
        )
        
        # ایجاد پرداخت
        self.payment = Payment.objects.create(
            order=self.order,
            amount=150000,
            status='successful',
            payment_method='online',
            transaction_id='TRX12345',
        )
        
        # ایجاد اعلان
        self.notification = Notification.objects.create(
            title='پیام آزمایشی',
            message='این یک پیام آزمایشی است',
            type='info',
            user=self.normal_user,
        )
        
        self.notification_all = Notification.objects.create(
            title='پیام عمومی',
            message='این یک پیام عمومی است',
            type='info',
            all_users=True,
        )
        
        # ایجاد طرح
        self.design = Design.objects.create(
            user=self.normal_user,
            title='طرح آزمایشی',
            description='این یک طرح آزمایشی است',
        )
        
        # ایجاد چت
        self.chat_session = ChatSession.objects.create(
            user=self.normal_user,
            agent=self.admin_user,
            title='چت آزمایشی',
        )
        
        self.chat_message = ChatMessage.objects.create(
            chat_session=self.chat_session,
            sender=self.normal_user,
            message='سلام، من یک سوال دارم',
        )
        
        # ایجاد تنظیمات تبلیغات
        SystemSetting.objects.create(key='promo_1_title', value='تبلیغ آزمایشی', is_active=True)
        SystemSetting.objects.create(key='promo_1_image', value='/static/images/promo1.jpg', is_active=True)
        SystemSetting.objects.create(key='promo_1_link', value='/promo/1', is_active=True)
        
        # تنظیم API client
        self.client = APIClient()
    
    def test_main_summary_view_admin(self):
        """تست دریافت خلاصه صفحه اصلی برای کاربر مدیر"""
        # لاگین با کاربر مدیر
        self.client.force_authenticate(user=self.admin_user)
        
        # درخواست به API
        url = reverse('main:main_summary')
        response = self.client.get(url)
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی وجود کلیدهای اصلی در پاسخ
        self.assertIn('summary', response.data)
        self.assertIn('promotions', response.data)
        self.assertIn('navigation', response.data)
        
        # بررسی داده‌های خلاصه
        summary = response.data['summary']
        self.assertIn('order_count', summary)
        self.assertIn('payment_count', summary)
        self.assertIn('unread_notifications', summary)
        self.assertIn('recent_orders', summary)
        self.assertIn('recent_notifications', summary)
        self.assertIn('recent_designs', summary)
        self.assertIn('recent_chats', summary)
        
        # بررسی تعداد صحیح موارد
        self.assertEqual(summary['order_count'], 1)
        self.assertEqual(summary['payment_count'], 1)
        
        # بررسی تبلیغات
        promotions = response.data['promotions']
        self.assertEqual(len(promotions), 1)
        self.assertEqual(promotions[0]['title'], 'تبلیغ آزمایشی')
        
        # بررسی منوی ناوبری
        navigation = response.data['navigation']
        self.assertTrue(any(item['title'] == 'داشبورد' and item['visible'] is True for item in navigation))
        self.assertTrue(any(item['title'] == 'کاربران' and item['visible'] is True for item in navigation))
    
    def test_main_summary_view_normal_user(self):
        """تست دریافت خلاصه صفحه اصلی برای کاربر عادی"""
        # لاگین با کاربر عادی
        self.client.force_authenticate(user=self.normal_user)
        
        # درخواست به API
        url = reverse('main:main_summary')
        response = self.client.get(url)
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی داده‌های خلاصه
        summary = response.data['summary']
        
        # بررسی تعداد صحیح موارد
        self.assertEqual(summary['order_count'], 1)
        self.assertEqual(summary['payment_count'], 1)
        
        # بررسی اینکه کاربر عادی فقط سفارش‌های خودش را می‌بیند
        self.assertEqual(len(summary['recent_orders']), 1)
        
        # بررسی منوی ناوبری برای کاربر عادی (داشبورد و کاربران نباید نمایش داده شوند)
        navigation = response.data['navigation']
        self.assertTrue(any(item['title'] == 'داشبورد' and item['visible'] is False for item in navigation))
        self.assertTrue(any(item['title'] == 'کاربران' and item['visible'] is False for item in navigation))
        self.assertTrue(any(item['title'] == 'سفارش‌ها' and item['visible'] is True for item in navigation))
    
    def test_main_summary_view_unauthenticated(self):
        """تست دریافت خلاصه صفحه اصلی برای کاربر غیرمجاز"""
        # بدون لاگین
        url = reverse('main:main_summary')
        response = self.client.get(url)
        
        # بررسی عدم دسترسی
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_main_summary_with_days_parameter(self):
        """تست دریافت خلاصه صفحه اصلی با پارامتر days"""
        # لاگین با کاربر عادی
        self.client.force_authenticate(user=self.normal_user)
        
        # درخواست به API با پارامتر days=30
        url = reverse('main:main_summary') + '?days=30'
        response = self.client.get(url)
        
        # بررسی پاسخ
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی داده‌های خلاصه
        summary = response.data['summary']
        
        # بررسی تعداد صحیح موارد (باید همان مقادیر قبلی باشند چون داده‌های ما جدید هستند)
        self.assertEqual(summary['order_count'], 1)
        self.assertEqual(summary['payment_count'], 1)
