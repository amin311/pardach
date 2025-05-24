from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.authentication.models import User
from apps.business.models import Business
from .models import Notification, NotificationCategory
import uuid

@pytest.mark.django_db
class NotificationModelTests(TestCase):
    """تست‌های مدل‌های اپ Notification"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.business = Business.objects.create(
            name='کسب‌وکار تست',
            status='active',
            owner=self.user
        )
        self.category = NotificationCategory.objects.create(
            name='دسته‌بندی تست',
            description='توضیحات دسته‌بندی تست'
        )
        
    def test_category_creation(self):
        """تست ایجاد دسته‌بندی اعلان"""
        self.assertEqual(self.category.name, 'دسته‌بندی تست')
        self.assertEqual(self.category.description, 'توضیحات دسته‌بندی تست')
        
    def test_notification_creation(self):
        """تست ایجاد اعلان"""
        notification = Notification.objects.create(
            user=self.user,
            business=self.business,
            category=self.category,
            type='system',
            title='اعلان تست',
            content='محتوای اعلان تست',
            priority=2
        )
        
        self.assertEqual(notification.title, 'اعلان تست')
        self.assertEqual(notification.content, 'محتوای اعلان تست')
        self.assertEqual(notification.type, 'system')
        self.assertEqual(notification.priority, 2)
        self.assertEqual(notification.is_read, False)
        self.assertEqual(notification.is_archived, False)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.business, self.business)
        self.assertEqual(notification.category, self.category)

@pytest.mark.django_db
class NotificationAPITests(TestCase):
    """تست‌های API اپ Notification"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.business = Business.objects.create(
            name='کسب‌وکار تست',
            status='active',
            owner=self.user
        )
        self.category = NotificationCategory.objects.create(
            name='دسته‌بندی تست',
            description='توضیحات دسته‌بندی تست'
        )
        
    def test_list_notifications_authenticated(self):
        """تست دریافت لیست اعلانات برای کاربر احراز هویت شده"""
        self.client.force_authenticate(user=self.user)
        
        # ایجاد چند اعلان برای کاربر
        Notification.objects.create(
            user=self.user,
            type='system',
            title='اعلان 1',
            content='محتوای اعلان 1'
        )
        
        Notification.objects.create(
            user=self.user,
            type='order_status',
            title='اعلان 2',
            content='محتوای اعلان 2',
            is_read=True
        )
        
        # دریافت لیست اعلانات
        response = self.client.get(reverse('notification_list_create'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_list_notifications_unauthenticated(self):
        """تست دریافت لیست اعلانات برای کاربر بدون احراز هویت"""
        response = self.client.get(reverse('notification_list_create'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_notification_admin(self):
        """تست ایجاد اعلان توسط کاربر ادمین"""
        self.client.force_authenticate(user=self.admin_user)
        
        notification_data = {
            'user_id': self.user.id,
            'category_id': self.category.id,
            'type': 'system',
            'title': 'اعلان تست API',
            'content': 'محتوای اعلان تست API',
            'priority': 2
        }
        
        response = self.client.post(
            reverse('notification_list_create'),
            notification_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(Notification.objects.get().title, 'اعلان تست API')
        
    def test_create_notification_non_admin(self):
        """تست ایجاد اعلان توسط کاربر غیر ادمین (باید با خطا مواجه شود)"""
        self.client.force_authenticate(user=self.user)
        
        notification_data = {
            'user_id': self.user.id,
            'type': 'system',
            'title': 'اعلان تست API',
            'content': 'محتوای اعلان تست API'
        }
        
        response = self.client.post(
            reverse('notification_list_create'),
            notification_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_mark_notification_read(self):
        """تست علامت‌گذاری اعلان به عنوان خوانده شده"""
        self.client.force_authenticate(user=self.user)
        
        # ایجاد اعلان
        notification = Notification.objects.create(
            user=self.user,
            type='system',
            title='اعلان تست',
            content='محتوای اعلان تست'
        )
        
        # علامت‌گذاری اعلان
        response = self.client.post(
            reverse('notification_mark_read', kwargs={'notification_id': notification.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی اعمال تغییرات
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        
    def test_archive_notification(self):
        """تست آرشیو کردن اعلان"""
        self.client.force_authenticate(user=self.user)
        
        # ایجاد اعلان
        notification = Notification.objects.create(
            user=self.user,
            type='system',
            title='اعلان تست',
            content='محتوای اعلان تست'
        )
        
        # آرشیو کردن اعلان
        response = self.client.post(
            reverse('notification_archive', kwargs={'notification_id': notification.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی اعمال تغییرات
        notification.refresh_from_db()
        self.assertTrue(notification.is_archived)
