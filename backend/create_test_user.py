#!/usr/bin/env python
"""
اسکریپت ایجاد کاربر آزمایشی برای تست سیستم
"""
import os
import sys
import django

# تنظیم Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import Role
from apps.business.models import Business
from apps.print_locations.models import PrintCenter

User = get_user_model()

def create_test_data():
    """ایجاد داده‌های آزمایشی"""
    
    # ایجاد کاربر آزمایشی
    if not User.objects.filter(username='testuser').exists():
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='کاربر',
            last_name='آزمایشی'
        )
        print(f"✅ کاربر آزمایشی ایجاد شد: {user.username}")
    else:
        user = User.objects.get(username='testuser')
        print(f"ℹ️  کاربر آزمایشی موجود است: {user.username}")
    
    # ایجاد کاربر ادمین
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='مدیر',
            last_name='سیستم'
        )
        print(f"✅ کاربر ادمین ایجاد شد: {admin.username}")
    else:
        admin = User.objects.get(username='admin')
        print(f"ℹ️  کاربر ادمین موجود است: {admin.username}")
    
    # ایجاد نقش‌های پایه
    roles_data = [
        {'name': 'customer', 'description': 'مشتری'},
        {'name': 'business_owner', 'description': 'صاحب کسب‌وکار'},
        {'name': 'admin', 'description': 'مدیر سیستم'},
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        if created:
            print(f"✅ نقش ایجاد شد: {role.name}")
        else:
            print(f"ℹ️  نقش موجود است: {role.name}")
    
    # ایجاد کسب‌وکار نمونه
    if not Business.objects.filter(name='چاپخانه نمونه').exists():
        business = Business.objects.create(
            name='چاپخانه نمونه',
            owner=user,
            description='چاپخانه آزمایشی برای تست سیستم',
            status='active'
        )
        print(f"✅ کسب‌وکار نمونه ایجاد شد: {business.name}")
    else:
        print("ℹ️  کسب‌وکار نمونه موجود است")
    
    # ایجاد مکان‌های چاپ نمونه
    locations_data = [
        {
            'name': 'چاپخانه مرکزی',
            'address': 'تهران، خیابان ولیعصر، پلاک 100',
            'city': 'تهران',
            'phone': '021-88776655',
            'opening_hours': '8:00 - 20:00'
        },
        {
            'name': 'چاپخانه شعبه شمال',
            'address': 'تهران، خیابان شریعتی، پلاک 200',
            'city': 'تهران',
            'phone': '021-77665544',
            'opening_hours': '9:00 - 18:00'
        }
    ]
    
    for location_data in locations_data:
        location, created = PrintCenter.objects.get_or_create(
            name=location_data['name'],
            defaults=location_data
        )
        if created:
            print(f"✅ مکان چاپ ایجاد شد: {location.name}")
        else:
            print(f"ℹ️  مکان چاپ موجود است: {location.name}")

if __name__ == '__main__':
    print("🚀 ایجاد داده‌های آزمایشی...")
    create_test_data()
    print("✨ تمام داده‌های آزمایشی ایجاد شدند!")
    print("\n📋 اطلاعات ورود:")
    print("👤 کاربر عادی: testuser / testpass123")
    print("👨‍💼 ادمین: admin / admin123") 