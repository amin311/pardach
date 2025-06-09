from django.test import TestCase
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient
from .models import User, Role
from apps.core.utils import to_jalali
from django.urls import reverse
import uuid

# Create your tests here.

@pytest.mark.django_db
def test_create_user():
    """تست ایجاد کاربر عادی"""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='test123')
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.check_password('test123')
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser():
    """تست ایجاد کاربر ادمین"""
    superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
    assert superuser.is_staff
    assert superuser.is_superuser
    assert superuser.is_active

@pytest.mark.django_db
def test_set_current_role():
    """تست تغییر نقش کاربر"""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='test123')
    role = Role.objects.create(name='customer', description='مشتری')
    assert user.set_current_role('customer')
    assert user.current_role == role
    assert not user.set_current_role('nonexistent')

@pytest.mark.django_db
def test_auth_api_register(client):
    """تست API ثبت‌نام"""
    response = client.post('/api/auth/register/', {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'test123',
        'first_name': 'Test',
        'last_name': 'User'
    })
    assert response.status_code == 201
    assert 'access' in response.data
    assert response.data['user']['username'] == 'testuser'

@pytest.mark.django_db
def test_auth_api_login(client):
    """تست API ورود"""
    # ایجاد کاربر برای تست
    User.objects.create_user(username='testuser', email='test@example.com', password='test123')
    
    response = client.post('/api/auth/login/', {
        'username': 'testuser',
        'password': 'test123'
    })
    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_user_crud_admin(client):
    """تست CRUD کاربران توسط ادمین"""
    # ایجاد ادمین و کاربر عادی
    admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
    
    # استفاده از APIClient برای دسترسی ادمین
    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)
    
    # تست ایجاد کاربر
    user_data = {
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123',
        'first_name': 'New',
        'last_name': 'User'
    }
    response = admin_client.post('/api/auth/users/', user_data)
    assert response.status_code == 201
    
    # تست دریافت لیست کاربران
    response = admin_client.get('/api/auth/users/')
    assert response.status_code == 200
    assert len(response.data) == 2  # admin و کاربر جدید
    
    # تست ویرایش کاربر
    user_id = response.data[1]['id']  # شناسه کاربر جدید
    update_data = {'first_name': 'Updated'}
    response = admin_client.put(f'/api/auth/users/{user_id}/', update_data)
    assert response.status_code == 200
    assert response.data['first_name'] == 'Updated'
    
    # تست حذف کاربر
    response = admin_client.delete(f'/api/auth/users/{user_id}/')
    assert response.status_code == 204
    
    # تست تعداد کاربران بعد از حذف
    response = admin_client.get('/api/auth/users/')
    assert len(response.data) == 1

@pytest.mark.django_db
def test_role_operations(client):
    """تست عملیات مربوط به نقش‌ها"""
    # ایجاد ادمین
    admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
    
    # استفاده از APIClient برای دسترسی ادمین
    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)
    
    # ایجاد چند permission برای تست
    perm1 = Permission.objects.get_or_create(
        codename='view_designs',
        defaults={'name': 'Can view designs', 'content_type_id': 1}
    )[0]
    perm2 = Permission.objects.get_or_create(
        codename='create_orders', 
        defaults={'name': 'Can create orders', 'content_type_id': 1}
    )[0]
    
    # تست ایجاد نقش
    role_data = {
        'name': 'business',
        'description': 'کاربر کسب و کار',
        'permissions': [perm1.id, perm2.id]
    }
    response = admin_client.post('/api/auth/roles/', role_data)
    assert response.status_code == 201
    
    # بررسی اینکه permissions به درستی اختصاص یافته
    role = Role.objects.get(name='business')
    assert role.permissions.count() == 2
    assert perm1 in role.permissions.all()
    assert perm2 in role.permissions.all()
    
    # تست دریافت لیست نقش‌ها
    response = admin_client.get('/api/auth/roles/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'business'
    assert 'permissions_list' in response.data[0]
    
    # تست تغییر نقش کاربر
    admin_client.post('/api/auth/set-role/', {'role_name': 'business'})
    admin.refresh_from_db()
    assert admin.current_role.name == 'business'
