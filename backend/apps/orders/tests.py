from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Order, OrderItem
from apps.authentication.models import User
from apps.designs.models import Design
from apps.templates_app.models import UserTemplate
import uuid

class OrderModelTest(TestCase):
    """تست‌های مدل سفارش"""
    
    def setUp(self):
        """راه‌اندازی داده‌های آزمایشی"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
    def test_order_creation(self):
        """تست ایجاد سفارش"""
        order = Order.objects.create(
            user=self.user,
            status='pending',
            notes='تست سفارش'
        )
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.notes, 'تست سفارش')
        self.assertEqual(order.total_price, 0)
        
    def test_order_str(self):
        """تست نمایش رشته‌ای سفارش"""
        order = Order.objects.create(
            user=self.user,
            status='pending'
        )
        
        self.assertIn(str(order.id)[:8], str(order))
        self.assertIn(self.user.username, str(order))
        
    def test_calculate_total_price(self):
        """تست محاسبه قیمت کل سفارش"""
        order = Order.objects.create(
            user=self.user,
            status='pending'
        )
        
        design = Design.objects.create(
            title='طرح تست',
            description='توضیحات تست',
            price=1000,
            created_by=self.user
        )
        
        OrderItem.objects.create(
            order=order,
            design=design,
            quantity=2,
            price=2000
        )
        
        OrderItem.objects.create(
            order=order,
            design=design,
            quantity=1,
            price=1000
        )
        
        total = order.calculate_total_price()
        self.assertEqual(total, 3000)
        self.assertEqual(order.total_price, 3000)

class OrderAPITest(TestCase):
    """تست‌های API سفارش"""
    
    def setUp(self):
        """راه‌اندازی داده‌های آزمایشی"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        self.admin = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123'
        )
        
        self.design = Design.objects.create(
            title='طرح تست',
            description='توضیحات تست',
            price=1000,
            created_by=self.user
        )
        
        self.order = Order.objects.create(
            user=self.user,
            status='pending',
            notes='تست سفارش'
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            design=self.design,
            quantity=2,
            price=2000
        )
        
    def test_list_orders(self):
        """تست دریافت لیست سفارش‌ها"""
        # تست با کاربر عادی
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # تست با کاربر ادمین
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_order(self):
        """تست ایجاد سفارش"""
        self.client.force_authenticate(user=self.user)
        data = {
            'status': 'pending',
            'notes': 'سفارش جدید تستی'
        }
        
        response = self.client.post('/api/orders/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['notes'], 'سفارش جدید تستی')
        self.assertEqual(response.data['user'], self.user.username)
        
    def test_get_order_detail(self):
        """تست دریافت جزئیات سفارش"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/orders/{self.order.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.order.id))
        
    def test_update_order(self):
        """تست به‌روزرسانی سفارش"""
        self.client.force_authenticate(user=self.user)
        data = {
            'status': 'processing',
            'notes': 'سفارش به‌روزرسانی شده'
        }
        
        response = self.client.put(f'/api/orders/{self.order.id}/', data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'processing')
        self.assertEqual(response.data['notes'], 'سفارش به‌روزرسانی شده')
        
    def test_delete_order(self):
        """تست حذف سفارش"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
        
    def test_create_order_item(self):
        """تست ایجاد آیتم سفارش"""
        self.client.force_authenticate(user=self.user)
        data = {
            'design_id': str(self.design.id),
            'quantity': 3
        }
        
        response = self.client.post(f'/api/orders/{self.order.id}/items/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 3)
        
        # بررسی به‌روزرسانی قیمت کل سفارش
        self.order.refresh_from_db()
        new_price = 2000 + (3 * 1000)  # قیمت آیتم قبلی + (تعداد * قیمت طرح)
        self.assertEqual(self.order.total_price, new_price)
