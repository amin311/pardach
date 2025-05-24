import os
import django
import random
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import sys
import traceback

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

# استفاده از مدل‌های پروژه
from apps.authentication.models import User
from django.contrib.auth.models import Group

def create_simple_test_data():
    print("در حال ایجاد داده‌های تستی پایه...")
    
    try:
        # ایجاد گروه‌های کاربری
        admin_group, _ = Group.objects.get_or_create(name='admin')
        business_owner_group, _ = Group.objects.get_or_create(name='business_owner')
        designer_group, _ = Group.objects.get_or_create(name='designer')
        customer_group, _ = Group.objects.get_or_create(name='customer')
        
        # ایجاد کاربران تستی
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'مدیر',
                'last_name': 'سیستم',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            admin_user.groups.add(admin_group)
            print(f"کاربر {admin_user.username} ایجاد شد.")
        else:
            print(f"کاربر {admin_user.username} از قبل وجود دارد.")
        
        business_owner, created = User.objects.get_or_create(
            username='business1',
            defaults={
                'email': 'business1@example.com',
                'first_name': 'مالک',
                'last_name': 'کسب‌وکار'
            }
        )
        
        if created:
            business_owner.set_password('business123')
            business_owner.save()
            business_owner.groups.add(business_owner_group)
            print(f"کاربر {business_owner.username} ایجاد شد.")
        else:
            print(f"کاربر {business_owner.username} از قبل وجود دارد.")
        
        designer, created = User.objects.get_or_create(
            username='designer1',
            defaults={
                'email': 'designer1@example.com',
                'first_name': 'طراح',
                'last_name': 'خلاق'
            }
        )
        
        if created:
            designer.set_password('designer123')
            designer.save()
            designer.groups.add(designer_group)
            print(f"کاربر {designer.username} ایجاد شد.")
        else:
            print(f"کاربر {designer.username} از قبل وجود دارد.")
        
        customer1, created = User.objects.get_or_create(
            username='customer1',
            defaults={
                'email': 'customer1@example.com',
                'first_name': 'مشتری',
                'last_name': 'اول'
            }
        )
        
        if created:
            customer1.set_password('customer123')
            customer1.save()
            customer1.groups.add(customer_group)
            print(f"کاربر {customer1.username} ایجاد شد.")
        else:
            print(f"کاربر {customer1.username} از قبل وجود دارد.")
            
        print("داده‌های تستی پایه با موفقیت ایجاد شدند.")
        
    except Exception as e:
        print(f"خطا در ایجاد داده‌های تستی: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    create_simple_test_data() 