# راهنمای مدیریت مایگریشن‌های Django

## مشکل اصلی
خطاهای `OperationalError: no such table` به دلیل عدم اعمال مایگریشن‌ها روی پایگاه داده رخ می‌دهد.

## راه‌حل کامل (انجام شده)

### 1. اضافه کردن همه‌ی اپ‌ها به INSTALLED_APPS
```python
# backend/config/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.authentication',
    'apps.business',
    'apps.orders',
    'apps.core',
    'apps.tender',
    'apps.print_locations',
    'apps.craft',
    'apps.main',
    'apps.communication',
    'apps.reports',
    'apps.templates_app',
    'apps.set_design',
    'apps.api',
    'apps.notification',
    'apps.payment',
    'apps.designs',
    'apps.workshop',
    'apps.settings',
    'apps.dashboard',
]
```

### 2. تولید مایگریشن‌ها برای همه‌ی اپ‌ها
```bash
cd backend
python manage.py makemigrations
```

### 3. اعمال همه‌ی مایگریشن‌ها
```bash
python manage.py migrate
```

## استفاده از اسکریپت خودکار

### Windows
```bash
.\manage_migrations.bat
```

## دستورات مفید

### بررسی وضعیت مایگریشن‌ها
```bash
python manage.py showmigrations
```

### تولید مایگریشن برای اپ خاص
```bash
python manage.py makemigrations app_name
```

### اعمال مایگریشن اپ خاص
```bash
python manage.py migrate app_name
```

### بررسی تغییرات بدون اعمال
```bash
python manage.py makemigrations --dry-run --check
```

## قوانین تیمی

### ✅ کارهای ضروری
- همیشه قبل از commit کردن: `python manage.py makemigrations`
- همیشه بعد از pull کردن: `python manage.py migrate`
- قبل از اجرای سرور: `python manage.py migrate`

### ❌ کارهای ممنوع
- commit کردن بدون بررسی مایگریشن‌ها
- حذف فایل‌های مایگریشن بدون هماهنگی
- ویرایش مستقیم فایل‌های مایگریشن

## رفع مشکلات رایج

### خطای InconsistentMigrationHistory
```bash
# محیط توسعه
del db.sqlite3
python manage.py migrate

# محیط تولید
python manage.py migrate --fake-initial
```

### مایگریشن خالی یا آسیب‌دیده
```bash
# حذف فایل آسیب‌دیده
del apps\app_name\migrations\0001_initial.py
# تولید مجدد
python manage.py makemigrations app_name
```

## وضعیت فعلی پروژه

همه‌ی اپ‌های زیر مایگریشن دارند و اعمال شده‌اند:
- ✅ authentication
- ✅ business  
- ✅ orders
- ✅ core
- ✅ tender
- ✅ print_locations
- ✅ craft
- ✅ main
- ✅ communication
- ✅ reports
- ✅ templates_app
- ✅ set_design
- ✅ api
- ✅ notification
- ✅ payment
- ✅ designs

اپ‌های بدون مدل (مایگریشن ندارند):
- dashboard
- settings  
- workshop

## نتیجه‌گیری
با اجرای این راهکار، تمام خطاهای "no such table" برطرف شده‌اند و سیستم آماده استفاده است. 