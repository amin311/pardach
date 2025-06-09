#!/usr/bin/env python
"""
تست ساده برای Backend
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# تنظیم Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

def test_django_setup():
    """تست راه‌اندازی Django"""
    print("🧪 تست راه‌اندازی Django...")
    try:
        from django.contrib.auth.models import User
        print("✅ Django models قابل import هستند")
        
        # تست database connection
        users_count = User.objects.count()
        print(f"✅ Database connection موفق - کاربران موجود: {users_count}")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست Django: {e}")
        return False

def test_apps_import():
    """تست import کردن apps"""
    print("🧪 تست import apps...")
    
    apps_to_test = [
        'apps.core',
        'apps.authentication', 
        'apps.main',
        'apps.designs',
        'apps.orders'
    ]
    
    success_count = 0
    for app in apps_to_test:
        try:
            __import__(app)
            print(f"✅ {app} - موفق")
            success_count += 1
        except Exception as e:
            print(f"❌ {app} - خطا: {e}")
    
    print(f"📊 {success_count}/{len(apps_to_test)} apps موفق")
    return success_count == len(apps_to_test)

def test_basic_urls():
    """تست basic URL patterns"""
    print("🧪 تست URL patterns...")
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # تست admin
        response = client.get('/admin/')
        print(f"✅ Admin URL - Status: {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ خطا در تست URLs: {e}")
        return False

def main():
    """اجرای تمام تست‌ها"""
    print("🚀 شروع تست‌های ساده Backend")
    print("=" * 50)
    
    results = []
    
    # تست Django setup
    results.append(test_django_setup())
    
    # تست apps
    results.append(test_apps_import())
    
    # تست URLs
    results.append(test_basic_urls())
    
    print("\n" + "=" * 50)
    print("📋 خلاصه نتایج:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ تست‌های موفق: {passed}")
    print(f"📝 کل تست‌ها: {total}")
    print(f"📈 نرخ موفقیت: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 تمام تست‌ها موفق بودند!")
        return True
    else:
        print("\n⚠️ برخی تست‌ها ناموفق بودند")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 