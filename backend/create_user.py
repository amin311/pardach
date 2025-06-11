import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

User = get_user_model()

# ایجاد کاربر تست
try:
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
    print(f"کاربر ایجاد شد: {user.username}")
except Exception as e:
    print(f"خطا: {e}")

# ایجاد ادمین
try:
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
    print(f"ادمین ایجاد شد: {admin.username}")
except Exception as e:
    print(f"خطا: {e}")

print("کاربران موجود:")
for u in User.objects.all():
    print(f"- {u.username} ({u.email})") 