import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import SiteSetting, HomeBlock

def create_initial_data():
    # ایجاد تنظیمات سایت
    SiteSetting.objects.get_or_create(
        key='require_signup_for_home',
        defaults={'value': {'require_signup_for_home': False}}
    )

    # ایجاد بلوک‌های صفحه اصلی
    blocks = [
        {
            'title': 'به فروشگاه ما خوش آمدید',
            'type': HomeBlock.VIDEO_BANNER,
            'config': {'videoUrl': '/media/welcome.mp4'},
            'order': 1,
            'is_active': True
        },
        {
            'title': 'محصولات ما',
            'type': HomeBlock.CATALOG_LINK,
            'config': {'url': '/catalog'},
            'order': 2,
            'is_active': True
        },
        {
            'title': 'سفارش آنلاین',
            'type': HomeBlock.ORDER_FORM,
            'config': {},
            'order': 3,
            'is_active': True
        },
        {
            'title': 'کسب‌وکارهای ما',
            'type': HomeBlock.BUSINESS_GRID,
            'config': {},
            'order': 4,
            'is_active': True
        }
    ]

    for block_data in blocks:
        HomeBlock.objects.get_or_create(
            title=block_data['title'],
            defaults=block_data
        )

if __name__ == '__main__':
    create_initial_data()
    print('داده‌های اولیه با موفقیت ایجاد شدند.') 