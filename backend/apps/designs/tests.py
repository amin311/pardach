import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Tag, DesignCategory, Family, Design, FamilyDesignRequirement, DesignFamily
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import uuid

@pytest.mark.django_db
def test_tag_model():
    """تست مدل برچسب‌ها"""
    tag = Tag.objects.create(name='تست', slug='test')
    assert str(tag) == 'تست'
    assert tag.designs_count == 0

@pytest.mark.django_db
def test_design_category_model():
    """تست مدل دسته‌بندی"""
    parent = DesignCategory.objects.create(name='دسته والد', slug='parent')
    child = DesignCategory.objects.create(name='دسته فرزند', slug='child', parent=parent)
    
    assert str(parent) == 'دسته والد'
    assert parent.designs_count == 0
    assert parent.children_count == 1
    assert parent.is_root == True
    assert child.is_root == False
    assert child.full_path == 'دسته والد > دسته فرزند'

@pytest.mark.django_db
def test_family_model():
    """تست مدل خانواده"""
    family = Family.objects.create(name='خانواده تست', slug='test-family')
    assert str(family) == 'خانواده تست'
    assert family.designs_count == 0

@pytest.mark.django_db
def test_design_model():
    """تست مدل طرح"""
    design = Design.objects.create(
        title='طرح تست',
        type='vector',
    )
    
    assert str(design) == 'طرح تست'
    assert design.status == 'draft'
    assert design.is_public == True
    assert design.view_count == 0
    assert design.download_count == 0
    
    # تست متدهای increment
    design.increment_view_count()
    assert design.view_count == 1
    
    design.increment_download_count()
    assert design.download_count == 1

@pytest.mark.django_db
def test_tags_api(client):
    """تست API برچسب‌ها"""
    user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
    client = APIClient()
    client.force_login(user)
    
    # تست ایجاد برچسب
    response = client.post('/api/designs/tags/', {'name': 'برچسب تست', 'slug': 'test-tag'})
    assert response.status_code == 201
    
    # تست دریافت برچسب‌ها
    response = client.get('/api/designs/tags/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == 'برچسب تست'

@pytest.mark.django_db
def test_designs_api(client):
    """تست API طرح‌ها"""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
    client = APIClient()
    client.force_login(user)
    
    # تست ایجاد طرح
    image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    response = client.post('/api/designs/designs/', {
        'title': 'طرح تست',
        'type': 'vector',
        'product_image': image
    }, format='multipart')
    assert response.status_code == 201
    
    # تست دریافت لیست طرح‌ها
    response = client.get('/api/designs/designs/')
    assert response.status_code == 200
    assert len(response.data) == 1
    
    # تست دریافت جزئیات طرح
    design_id = response.data[0]['id']
    response = client.get(f'/api/designs/designs/{design_id}/')
    assert response.status_code == 200
    assert response.data['title'] == 'طرح تست'
    assert response.data['view_count'] == 1  # به خاطر increment_view_count
    
    # تست به‌روزرسانی طرح
    response = client.put(f'/api/designs/designs/{design_id}/', {
        'title': 'طرح به‌روز شده',
        'type': 'vector'
    })
    assert response.status_code == 200
    assert response.data['title'] == 'طرح به‌روز شده'
    
    # تست حذف طرح
    response = client.delete(f'/api/designs/designs/{design_id}/')
    assert response.status_code == 204
    
    # تأیید حذف
    response = client.get('/api/designs/designs/')
    assert len(response.data) == 0

@pytest.mark.django_db
def test_batch_upload_api(client):
    """تست API آپلود دسته‌ای"""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
    client = APIClient()
    client.force_login(user)
    
    # ایجاد چند فایل تستی
    image1 = SimpleUploadedFile("test1.jpg", b"file_content", content_type="image/jpeg")
    image2 = SimpleUploadedFile("test2.jpg", b"file_content", content_type="image/jpeg")
    
    response = client.post('/api/designs/batch-upload/', {
        'design_files': [image1, image2],
        'type': 'vector',
        'status': 'draft',
        'is_public': True
    }, format='multipart')
    
    assert response.status_code == 201
    assert len(response.data) == 2
    assert response.data[0]['title'] == 'test1'
    assert response.data[1]['title'] == 'test2'
