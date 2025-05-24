import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from .models import SystemSetting
from .utils import to_jalali, validate_file_size, validate_file_format, get_system_setting
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from datetime import datetime

@pytest.mark.django_db
def test_system_setting_create():
    """تست ایجاد یک تنظیم سیستم"""
    setting = SystemSetting.objects.create(key='max_file_size_mb', value=5, description='حداکثر حجم فایل')
    assert setting.key == 'max_file_size_mb'
    assert setting.value == 5
    assert setting.description == 'حداکثر حجم فایل'

@pytest.mark.django_db
def test_system_setting_api(client):
    """تست APIهای تنظیمات سیستم"""
    user = User.objects.create_superuser(username='admin', password='admin123')
    client = APIClient()
    client.force_login(user)
    
    # تست ایجاد
    response = client.post('/api/core/settings/', {
        'key': 'max_file_size_mb',
        'value': 5,
        'description': 'حداکثر حجم فایل'
    })
    assert response.status_code == 201
    assert response.data['key'] == 'max_file_size_mb'

    # تست دریافت
    response = client.get('/api/core/settings/')
    assert response.status_code == 200
    assert len(response.data) == 1

    # تست به‌روزرسانی
    response = client.put('/api/core/settings/max_file_size_mb/', {'value': 10})
    assert response.status_code == 200
    assert response.data['value'] == 10

@pytest.mark.django_db
def test_to_jalali():
    """تست تبدیل تاریخ میلادی به شمسی"""
    date = datetime(2023, 4, 25, 12, 0)
    jalali_date = to_jalali(date)
    assert '1402/02/05' in jalali_date

@pytest.mark.django_db
def test_validate_file_size():
    """تست اعتبارسنجی حجم فایل"""
    file = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
    file.size = 2 * 1024 * 1024  # 2MB
    validated_file = validate_file_size(file, max_size_mb=5)
    assert validated_file == file

    file.size = 6 * 1024 * 1024  # 6MB
    with pytest.raises(ValidationError):
        validate_file_size(file, max_size_mb=5)

@pytest.mark.django_db
def test_validate_file_format():
    """تست اعتبارسنجی فرمت فایل"""
    file = SimpleUploadedFile('test.jpg', b'file_content', content_type='image/jpeg')
    validated_file = validate_file_format(file, allowed_formats=['jpg', 'png'])
    assert validated_file == file

    file = SimpleUploadedFile('test.txt', b'file_content', content_type='text/plain')
    with pytest.raises(ValidationError):
        validate_file_format(file, allowed_formats=['jpg', 'png'])

@pytest.mark.django_db
def test_get_system_setting():
    """تست دریافت تنظیمات سیستم"""
    SystemSetting.objects.create(key='max_file_size_mb', value=5)
    value = get_system_setting('max_file_size_mb')
    assert value == 5
    default_value = get_system_setting('non_existent_key', 10)
    assert default_value == 10
