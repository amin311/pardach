import os
import django
import random
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import sys
import traceback
from django.contrib.auth import get_user_model

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

# استفاده از مدل‌های پروژه
from apps.business.models import Business, BusinessUser
from apps.designs.models import Design, DesignCategory
from apps.orders.models import Order, OrderItem
from apps.designs.models import PrintLocation
from django.contrib.auth.models import Group

def create_test_data():
    print("در حال ایجاد داده‌های تستی...")
    
    try:
        # پاک کردن داده‌های موجود
        print("پاک کردن داده‌های موجود...")
        Order.objects.all().delete()
        Design.objects.all().delete()
        PrintLocation.objects.all().delete()
        DesignCategory.objects.all().delete()
        BusinessUser.objects.all().delete()
        Business.objects.all().delete()
        User.objects.filter(username__in=['admin', 'business1', 'designer1', 'customer1', 'customer2']).delete()
        
        # ایجاد گروه‌های کاربری
        admin_group, _ = Group.objects.get_or_create(name='admin')
        business_owner_group, _ = Group.objects.get_or_create(name='business_owner')
        designer_group, _ = Group.objects.get_or_create(name='designer')
        customer_group, _ = Group.objects.get_or_create(name='customer')
        
        # ایجاد کاربران تستی
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='مدیر',
            last_name='سیستم',
            is_staff=True,
            is_superuser=True
        )
        admin_user.groups.add(admin_group)
        
        business_owner = User.objects.create_user(
            username='business1',
            email='business1@example.com',
            password='business123',
            first_name='مالک',
            last_name='کسب‌وکار'
        )
        business_owner.groups.add(business_owner_group)
        
        designer = User.objects.create_user(
            username='designer1',
            email='designer1@example.com',
            password='designer123',
            first_name='طراح',
            last_name='خلاق'
        )
        designer.groups.add(designer_group)
        
        customer1 = User.objects.create_user(
            username='customer1',
            email='customer1@example.com',
            password='customer123',
            first_name='مشتری',
            last_name='اول'
        )
        customer1.groups.add(customer_group)
        
        customer2 = User.objects.create_user(
            username='customer2',
            email='customer2@example.com',
            password='customer123',
            first_name='مشتری',
            last_name='دوم'
        )
        customer2.groups.add(customer_group)
        
        # ایجاد کسب‌وکارها
        business1 = Business.objects.create(
            name='چاپخانه نمونه',
            owner=business_owner,
            description='چاپخانه تخصصی لباس و پارچه',
            status='active'
        )
        
        # اضافه کردن کاربر طراح به کسب‌وکار
        BusinessUser.objects.create(
            business=business1,
            user=designer,
            role='employee'
        )
        
        # ایجاد دسته‌بندی‌های طرح
        category1 = DesignCategory.objects.create(name='لوگو')
        category2 = DesignCategory.objects.create(name='طرح‌های تی‌شرت')
        
        # ایجاد محل‌های چاپ
        location1 = PrintLocation.objects.create(name='جلوی تی‌شرت')
        location2 = PrintLocation.objects.create(name='پشت تی‌شرت')
        location3 = PrintLocation.objects.create(name='آستین')
        
        # ایجاد طرح‌ها
        designs = []
        for i in range(1, 6):
            try:
                design = Design.objects.create(
                    title=f'طرح شماره {i}',
                    description=f'توضیحات طرح شماره {i}',
                    designer=designer,
                    business=business1,
                    is_public=True,
                    price=Decimal(random.randint(50000, 200000))
                )
                design.categories.add(random.choice([category1, category2]))
                design.suitable_locations.add(random.choice([location1, location2, location3]))
                designs.append(design)
            except Exception as e:
                print(f"خطا در ایجاد طرح {i}: {str(e)}")
                traceback.print_exc()
        
        # ایجاد سفارش‌ها
        for i in range(1, 4):
            try:
                customer = random.choice([customer1, customer2])
                order = Order.objects.create(
                    customer=customer,
                    business=business1,
                    status=random.choice(['draft', 'pending', 'confirmed', 'in_progress']),
                    garment_size=random.choice(['S', 'M', 'L', 'XL']),
                    fabric_type=random.choice(['cotton', 'polyester', 'cotton_polyester']),
                    fabric_color=random.choice(['سفید', 'مشکی', 'آبی', 'قرمز']),
                    fabric_weight=random.randint(120, 250),
                    total_price=Decimal(0),  # مقدار اولیه قبل از محاسبه
                    delivery_date=timezone.now().date() + timedelta(days=random.randint(7, 30)),
                    customer_notes=f'یادداشت‌های مشتری برای سفارش {i}'
                )
                
                # ایجاد آیتم‌های سفارش
                for j in range(1, random.randint(2, 4)):
                    design = random.choice(designs)
                    quantity = random.randint(10, 100)
                    unit_price = design.price
                    
                    OrderItem.objects.create(
                        order=order,
                        design=design,
                        quantity=quantity,
                        unit_price=unit_price,
                        print_location=random.choice([location1, location2, location3]),
                        print_dimensions=f'{random.randint(10, 30)}x{random.randint(10, 30)} سانتی‌متر',
                        color_count=random.randint(1, 4),
                        notes=f'توضیحات آیتم {j} از سفارش {i}'
                    )
                
                # محاسبه قیمت کل سفارش
                order.calculate_total_price()
            except Exception as e:
                print(f"خطا در ایجاد سفارش {i}: {str(e)}")
                traceback.print_exc()
            
        print("داده‌های تستی با موفقیت ایجاد شدند.")
        
    except Exception as e:
        print(f"خطا در ایجاد داده‌های تستی: {str(e)}")
        traceback.print_exc()

if __name__ == '__main__':
    create_test_data() 