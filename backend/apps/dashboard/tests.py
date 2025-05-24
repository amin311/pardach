from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.orders.models import Order
from apps.payment.models import Payment
from apps.notification.models import Notification
from apps.reports.models import Report
from apps.business.models import Business
from datetime import datetime
from apps.business.models import BusinessActivity

User = get_user_model()

@pytest.mark.django_db
class TestDashboardSummary:
    """تست‌های API داشبورد"""
    
    def setup_method(self):
        """تنظیمات اولیه تست"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='test123'
        )
        
        self.business = Business.objects.create(
            name='تست کسب‌وکار',
            owner=self.user
        )
        
        # ایجاد سفارش نمونه
        Order.objects.create(
            user=self.user,
            total_price=10000,
            created_at=datetime.now()
        )
        
        # ایجاد پرداخت نمونه
        Payment.objects.create(
            user=self.user,
            amount=10000,
            status='successful',
            created_at=datetime.now()
        )
        
        # ایجاد اعلان نمونه
        Notification.objects.create(
            user=self.user,
            type='system',
            title='تست',
            content='تست اعلان',
            created_at=datetime.now()
        )
        
        # ایجاد گزارش نمونه
        Report.objects.create(
            user=self.user,
            type='sales',
            title='گزارش تست',
            data={'labels': [], 'values': []},
            created_at=datetime.now()
        )
    
    def test_dashboard_summary_authenticated(self):
        """تست دریافت خلاصه داشبورد برای کاربر احراز هویت شده"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('dashboard:dashboard_summary')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert 'charts' in response.data
        assert response.data['summary']['order_count'] == 1
        assert response.data['summary']['total_sales'] == 10000
        assert response.data['summary']['payment_count'] == 1
        assert response.data['summary']['unread_notifications'] == 1
        assert response.data['summary']['report_count'] == 1
    
    def test_dashboard_summary_unauthenticated(self):
        """تست دریافت خلاصه داشبورد برای کاربر بدون احراز هویت"""
        url = reverse('dashboard:dashboard_summary')
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_summary_admin_view(self):
        """تست دسترسی ادمین به اطلاعات همه کاربران"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get('/api/dashboard/summary/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('summary', response.data)
        self.assertIn('charts', response.data)
    
    def test_business_detail_view(self):
        """تست دریافت خلاصه اطلاعات کسب‌وکارها"""
        self.client.force_authenticate(user=self.user)
        
        # ایجاد کسب‌وکار تست
        business = Business.objects.create(
            name='کسب‌وکار تست داشبورد',
            owner=self.user,
            status='active'
        )
        
        # ایجاد فعالیت کسب‌وکار
        BusinessActivity.objects.create(
            business=business,
            activity_type='design_sale',
            details={'amount': 15000}
        )
        
        response = self.client.get('/api/dashboard/business-detail/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_businesses', response.data)
        self.assertIn('active_businesses', response.data)
        self.assertIn('recent_activities', response.data)
        self.assertIn('top_performing_businesses', response.data)
        
        # بررسی مقادیر
        self.assertGreaterEqual(response.data['total_businesses'], 1)
        self.assertGreaterEqual(response.data['active_businesses'], 1)
        self.assertEqual(len(response.data['recent_activities']), 1)
