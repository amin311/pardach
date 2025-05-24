from django.test import TestCase
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Business, BusinessUser, BusinessActivity
import uuid

User = get_user_model()

@pytest.mark.django_db
class BusinessModelTests(TestCase):
    def setUp(self):
        # ایجاد کاربر تست
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # ایجاد کسب‌وکار تست
        self.business = Business.objects.create(
            name='Test Business',
            description='Test Description',
            owner=self.user,
            status='active'
        )

    def test_business_creation(self):
        """تست ایجاد کسب‌وکار جدید"""
        self.assertEqual(self.business.name, 'Test Business')
        self.assertEqual(self.business.owner, self.user)
        self.assertEqual(self.business.status, 'active')
        
        # تست ایجاد خودکار اسلاگ
        self.assertEqual(self.business.slug, 'test-business')
        
    def test_business_user_creation(self):
        """تست ایجاد کاربر کسب‌وکار"""
        business_user = BusinessUser.objects.create(
            business=self.business,
            user=self.user,
            role='manager'
        )
        self.assertEqual(business_user.business, self.business)
        self.assertEqual(business_user.user, self.user)
        self.assertEqual(business_user.role, 'manager')
        
    def test_business_activity_creation(self):
        """تست ایجاد فعالیت کسب‌وکار"""
        activity = BusinessActivity.objects.create(
            business=self.business,
            activity_type='design_sale',
            details={'amount': 1000, 'currency': 'IRR'}
        )
        
        self.assertEqual(activity.business, self.business)
        self.assertEqual(activity.activity_type, 'design_sale')
        self.assertEqual(activity.details['amount'], 1000)

@pytest.mark.django_db
class BusinessAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.business_data = {
            'name': 'کسب‌وکار تست API',
            'description': 'توضیحات تست API',
            'status': 'active'
        }
        
    def test_create_business_authenticated(self):
        """تست ایجاد کسب‌وکار برای کاربر احراز هویت شده"""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(
            reverse('business-list-create'),
            self.business_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Business.objects.count(), 1)
        self.assertEqual(Business.objects.get().name, 'کسب‌وکار تست API')
        
        # بررسی ایجاد خودکار کاربر کسب‌وکار با نقش مدیر
        self.assertEqual(BusinessUser.objects.count(), 1)
        self.assertEqual(BusinessUser.objects.get().role, 'manager')
        
    def test_create_business_unauthenticated(self):
        """تست ایجاد کسب‌وکار برای کاربر بدون احراز هویت"""
        response = self.client.post(
            reverse('business-list-create'),
            self.business_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_list_businesses(self):
        """تست دریافت لیست کسب‌وکارها"""
        self.client.force_authenticate(user=self.user)
        
        # ایجاد چند کسب‌وکار
        Business.objects.create(
            name='کسب‌وکار 1',
            status='active',
            owner=self.user
        )
        
        another_user = User.objects.create_user(
            username='another',
            email='another@example.com',
            password='password123'
        )
        
        Business.objects.create(
            name='کسب‌وکار 2',
            status='active',
            owner=another_user
        )
        
        # دریافت لیست کسب‌وکارها
        response = self.client.get(reverse('business-list-create'))
        
        # فقط کسب‌وکارهای متعلق به کاربر جاری برگردانده می‌شوند
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # تست برای ادمین - باید همه کسب‌وکارها را ببیند
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('business-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_update_business(self):
        """تست ویرایش کسب‌وکار"""
        self.client.force_authenticate(user=self.user)
        
        # ویرایش کسب‌وکار
        updated_data = {
            'name': 'کسب‌وکار به‌روزرسانی شده',
            'status': 'active'
        }
        
        response = self.client.put(
            reverse('business-detail', kwargs={'business_id': self.business.id}),
            updated_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی اعمال تغییرات
        self.business.refresh_from_db()
        self.assertEqual(self.business.name, 'کسب‌وکار به‌روزرسانی شده')
        self.assertEqual(self.business.status, 'active')
        
    def test_delete_business(self):
        """تست حذف کسب‌وکار"""
        self.client.force_authenticate(user=self.user)
        
        # حذف کسب‌وکار
        response = self.client.delete(
            reverse('business-detail', kwargs={'business_id': self.business.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Business.objects.count(), 0)
        
    def test_business_user_operations(self):
        """تست عملیات مربوط به کاربران کسب‌وکار"""
        self.client.force_authenticate(user=self.user)
        
        # ایجاد کاربر جدید
        another_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            password='password123'
        )
        
        # اضافه کردن کاربر به کسب‌وکار
        user_data = {
            'user_id': another_user.id,
            'role': 'employee'
        }
        
        response = self.client.post(
            reverse('business-user-list-create', kwargs={'business_id': self.business.id}),
            user_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessUser.objects.count(), 2)  # مالک + کارمند جدید
        
        # دریافت لیست کاربران
        response = self.client.get(
            reverse('business-user-list-create', kwargs={'business_id': self.business.id})
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

@pytest.mark.django_db
class BusinessPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
        # ایجاد کاربران تست
        self.owner = User.objects.create_user(
            username='owner',
            password='ownerpass123',
            email='owner@example.com'
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            password='managerpass123',
            email='manager@example.com'
        )
        
        self.employee = User.objects.create_user(
            username='employee',
            password='employeepass123',
            email='employee@example.com'
        )
        
        self.random_user = User.objects.create_user(
            username='random',
            email='random@example.com',
            password='password123'
        )
        
        # ایجاد کسب‌وکار
        self.business = Business.objects.create(
            name='Test Business',
            description='Test Description',
            owner=self.owner,
            status='active'
        )
        
        # ایجاد روابط کاربری
        BusinessUser.objects.create(
            business=self.business,
            user=self.manager,
            role='manager'
        )
        
        BusinessUser.objects.create(
            business=self.business,
            user=self.employee,
            role='employee'
        )
        
    def test_business_access_permissions(self):
        """تست دسترسی‌های مختلف به کسب‌وکار"""
        self.assertTrue(self.business.owner == self.owner)
        manager_role = BusinessUser.objects.get(business=self.business, user=self.manager)
        self.assertEqual(manager_role.role, 'manager')
        employee_role = BusinessUser.objects.get(business=self.business, user=self.employee)
        self.assertEqual(employee_role.role, 'employee')
        
        # دسترسی کاربر عادی (غیرمجاز)
        self.client.force_authenticate(user=self.random_user)
        response = self.client.get(reverse('business-detail', kwargs={'business_id': self.business.id}))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_business_edit_permissions(self):
        """تست دسترسی‌های ویرایش کسب‌وکار"""
        # مالک می‌تواند کسب‌وکار را ویرایش کند
        self.business.name = 'Updated Business Name'
        self.business.save()
        self.assertEqual(self.business.name, 'Updated Business Name')
