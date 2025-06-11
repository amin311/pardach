# اطلاعات دسترسی ادمین

## Superuser جدید ایجاد شده

**نام کاربری:** admin  
**ایمیل:** admin@example.com  
**رمز عبور:** [باید تنظیم شود]

## تنظیم رمز عبور

برای تنظیم رمز عبور superuser:

```bash
cd backend
python manage.py shell
```

سپس در shell پایتون:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('your_password_here')
admin.save()
exit()
```

یا استفاده از دستور:

```bash
python manage.py changepassword admin
```

## دسترسی به پنل ادمین

پس از تنظیم رمز عبور:

1. آدرس: `http://127.0.0.1:8000/admin/`
2. نام کاربری: `admin`
3. رمز عبور: همان که تنظیم کردید

## نکات مهم

- ⚠️ حتماً رمز عبور قوی انتخاب کنید
- 🔒 در محیط تولید از ایمیل واقعی استفاده کنید
- 📱 امکان تنظیم احراز هویت دوعاملی را در نظر بگیرید 