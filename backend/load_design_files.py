import os
import django
import shutil
from django.core.files import File
from django.utils.text import slugify
from pathlib import Path
import random
from django.contrib.auth import get_user_model

# تنظیم محیط جنگو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from apps.designs.models import Design, DesignCategory
User = get_user_model()
from apps.business.models import Business
from decimal import Decimal

def load_design_files():
    print("در حال بارگذاری فایل‌های طراحی...")
    
    try:
        # دریافت کاربر طراح و کسب‌وکار
        designer = User.objects.get(username='designer1')
        business = Business.objects.get(name='چاپخانه نمونه')
        
        # ایجاد دسته‌بندی‌های جدید
        logo_category = DesignCategory.objects.get_or_create(name='لوگو')[0]
        tshirt_category = DesignCategory.objects.get_or_create(name='طرح‌های تی‌شرت')[0]
        modern_category = DesignCategory.objects.get_or_create(name='طرح‌های مدرن')[0]
        abstract_category = DesignCategory.objects.get_or_create(name='طرح‌های انتزاعی')[0]
        
        # مسیر فایل‌های SVG
        svg_dir = Path('D:/Gpt engeeneir/sit8/svg format')
        ai_dir = Path('D:/Gpt engeeneir/sit8/set')
        
        # بارگذاری فایل‌های SVG
        for svg_file in svg_dir.glob('*.svg'):
            try:
                file_name = svg_file.stem
                title = f'طرح {file_name}'
                
                # ایجاد طرح جدید
                design = Design.objects.create(
                    title=title,
                    description=f'طرح SVG شماره {file_name}',
                    designer=designer,
                    business=business,
                    is_public=True,
                    price=Decimal(random.randint(50000, 200000)),
                    status='approved'
                )
                
                # افزودن فایل به طرح
                with open(svg_file, 'rb') as f:
                    design.file.save(f'{slugify(title)}.svg', File(f), save=True)
                
                # افزودن دسته‌بندی‌ها
                if int(file_name.replace('_', '')) % 2 == 0:
                    design.categories.add(logo_category)
                else:
                    design.categories.add(tshirt_category)
                
                if int(file_name.replace('_', '')) % 3 == 0:
                    design.categories.add(modern_category)
                if int(file_name.replace('_', '')) % 4 == 0:
                    design.categories.add(abstract_category)
                
                print(f"طرح {title} با موفقیت بارگذاری شد.")
                
            except Exception as e:
                print(f"خطا در بارگذاری {svg_file}: {str(e)}")
        
        # بارگذاری فایل‌های AI
        for ai_file in ai_dir.glob('*.ai'):
            try:
                file_name = ai_file.stem
                title = f'ست طراحی {file_name}'
                
                # ایجاد طرح جدید
                design = Design.objects.create(
                    title=title,
                    description=f'ست طراحی AI شماره {file_name}',
                    designer=designer,
                    business=business,
                    is_public=True,
                    price=Decimal(random.randint(200000, 500000)),
                    status='approved'
                )
                
                # افزودن فایل به طرح
                with open(ai_file, 'rb') as f:
                    design.file.save(f'{slugify(title)}.ai', File(f), save=True)
                
                # افزودن دسته‌بندی‌ها
                design.categories.add(modern_category)
                design.categories.add(abstract_category)
                
                print(f"ست طراحی {title} با موفقیت بارگذاری شد.")
                
            except Exception as e:
                print(f"خطا در بارگذاری {ai_file}: {str(e)}")
        
        print("بارگذاری فایل‌های طراحی با موفقیت انجام شد.")
        
    except Exception as e:
        print(f"خطا در بارگذاری فایل‌های طراحی: {str(e)}")

if __name__ == '__main__':
    load_design_files() 