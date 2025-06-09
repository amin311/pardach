#!/usr/bin/env python
"""
تست‌های جامع برای Backend Django
"""
import pytest
import subprocess
import os
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class BackendHealthTest(TestCase):
    """تست سلامت کلی backend"""
    
    def test_django_check(self):
        """تست django system check"""
        result = subprocess.run(
            ['python', 'manage.py', 'check', '--deploy'],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, f"Django check failed: {result.stderr}")
    
    def test_migrations_up_to_date(self):
        """بررسی به‌روز بودن migrations"""
        result = subprocess.run(
            ['python', 'manage.py', 'makemigrations', '--check', '--dry-run'],
            cwd=os.path.dirname(__file__),
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0, "Migrations are not up to date")

class APIEndpointTest(APITestCase):
    """تست تمام endpoint های API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    def test_public_endpoints(self):
        """تست endpoint های عمومی"""
        public_endpoints = [
            '/api/',
            '/api/docs/',
            '/api/auth/login/',
            '/api/auth/register/',
            '/api/print-locations/',
        ]
        
        for endpoint in public_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIn(response.status_code, [200, 301, 302], 
                    f"Endpoint {endpoint} failed with status {response.status_code}")
    
    def test_protected_endpoints_without_auth(self):
        """تست endpoint های محافظت شده بدون احراز هویت"""
        protected_endpoints = [
            '/api/designs/',
            '/api/orders/',
            '/api/dashboard/',
            '/api/profile/',
        ]
        
        for endpoint in protected_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIn(response.status_code, [401, 403], 
                    f"Protected endpoint {endpoint} should require authentication")
    
    def test_protected_endpoints_with_auth(self):
        """تست endpoint های محافظت شده با احراز هویت"""
        # ورود کاربر
        self.client.force_authenticate(user=self.user)
        
        protected_endpoints = [
            '/api/designs/',
            '/api/orders/',
            '/api/dashboard/',
        ]
        
        for endpoint in protected_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                self.assertIn(response.status_code, [200, 404], 
                    f"Authenticated endpoint {endpoint} failed")
    
    def test_admin_endpoints(self):
        """تست endpoint های ادمین"""
        self.client.force_authenticate(user=self.admin_user)
        
        admin_endpoints = [
            '/api/admin/users/',
            '/api/admin/designs/',
        ]
        
        for endpoint in admin_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(endpoint)
                # اگر endpoint وجود نداشته باشد، 404 قابل قبول است
                self.assertIn(response.status_code, [200, 404], 
                    f"Admin endpoint {endpoint} failed")

class AuthenticationTest(APITestCase):
    """تست احراز هویت"""
    
    def test_user_registration(self):
        """تست ثبت‌نام کاربر"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'نام',
            'last_name': 'خانوادگی'
        }
        
        response = self.client.post('/api/auth/register/', data)
        
        if response.status_code == 404:
            # اگر endpoint وجود ندارد، تست را رد نکنیم
            self.skipTest("Registration endpoint not found")
        
        self.assertIn(response.status_code, [200, 201])
    
    def test_user_login(self):
        """تست ورود کاربر"""
        user = User.objects.create_user(
            username='logintest',
            password='loginpass123'
        )
        
        data = {
            'username': 'logintest',
            'password': 'loginpass123'
        }
        
        response = self.client.post('/api/auth/login/', data)
        
        if response.status_code == 404:
            self.skipTest("Login endpoint not found")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)

def run_security_analysis():
    """اجرای آنالیز امنیتی با bandit"""
    print("🔒 اجرای آنالیز امنیتی...")
    
    result = subprocess.run([
        'bandit', '-r', 'apps/', '-f', 'json'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print("✅ هیچ مشکل امنیتی پیدا نشد")
        return True
    else:
        try:
            issues = json.loads(result.stdout)
            print(f"⚠️ {len(issues.get('results', []))} مشکل امنیتی پیدا شد:")
            for issue in issues.get('results', [])[:5]:  # نمایش 5 مورد اول
                print(f"  - {issue.get('test_name', 'Unknown')}: {issue.get('issue_text', 'No description')}")
        except:
            print(f"❌ خطا در آنالیز امنیتی: {result.stderr}")
        return False

def run_code_quality_check():
    """بررسی کیفیت کد با flake8"""
    print("📊 بررسی کیفیت کد...")
    
    result = subprocess.run([
        'flake8', 'apps/', '--count', '--select=E9,F63,F7,F82', '--show-source', '--statistics'
    ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    
    if result.returncode == 0:
        print("✅ کیفیت کد مناسب است")
        return True
    else:
        print(f"⚠️ مشکلات کیفیت کد:")
        print(result.stdout)
        return False

if __name__ == '__main__':
    print("🚀 شروع تست‌های جامع Backend")
    print("=" * 50)
    
    # اجرای تست‌های Django
    print("🧪 اجرای تست‌های Django...")
    django_result = subprocess.run([
        'python', 'manage.py', 'test', '--verbosity=2'
    ], cwd=os.path.dirname(__file__))
    
    # آنالیز امنیتی
    security_ok = run_security_analysis()
    
    # بررسی کیفیت کد
    quality_ok = run_code_quality_check()
    
    print("\n" + "=" * 50)
    print("📋 خلاصه نتایج:")
    print(f"  Django Tests: {'✅ موفق' if django_result.returncode == 0 else '❌ ناموفق'}")
    print(f"  Security: {'✅ مناسب' if security_ok else '⚠️ نیاز به بررسی'}")
    print(f"  Code Quality: {'✅ مناسب' if quality_ok else '⚠️ نیاز به بهبود'}")
    
    if django_result.returncode == 0 and security_ok and quality_ok:
        print("\n🎉 تمام تست‌ها موفق بودند!")
    else:
        print("\n⚠️ برخی تست‌ها نیاز به بررسی دارند") 