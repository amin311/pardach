#!/usr/bin/env python
import os
import sys
import django
from django.contrib.auth import get_user_model

# اضافه کردن مسیر backend به Python path
sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')

try:
    django.setup()
    User = get_user_model()
    
    # ایجاد کاربر تست
    user, created = User.objects.get_or_create(
        username='test',
        defaults={
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    user.set_password('test123')
    user.save()
    
    if created:
        print("✅ کاربر test ایجاد شد")
    else:
        print("ℹ️ کاربر test موجود بود و بروزرسانی شد")
    
    # ایجاد ادمین
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin.set_password('admin123')
    admin.save()
    
    if created:
        print("✅ ادمین admin ایجاد شد")
    else:
        print("ℹ️ ادمین admin موجود بود و بروزرسانی شد")
    
    print("\n📋 اطلاعات ورود:")
    print("👤 کاربر: test / test123")
    print("👨‍💼 ادمین: admin / admin123")
    
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc() 