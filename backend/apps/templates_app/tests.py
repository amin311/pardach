import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    Template, Section, DesignInput, Condition, UserTemplate,
    UserSection, UserDesignInput, UserCondition, SetDimensions
)

User = get_user_model()

class TemplateModelTests(TestCase):
    def setUp(self):
        # ایجاد یک کاربر برای تست
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # ایجاد یک قالب پایه برای تست
        self.template = Template.objects.create(
            title="تست قالب",
            description="توضیحات تست",
            base_price=1000,
            status=Template.Status.PUBLISHED,
            created_by=self.user
        )
        
        # ایجاد یک بخش برای تست
        self.section = Section.objects.create(
            template=self.template,
            title="بخش تست",
            description="توضیحات بخش تست",
            order=1
        )
        
        # ایجاد یک ورودی طرح برای تست
        self.design_input = DesignInput.objects.create(
            section=self.section,
            title="ورودی تست",
            description="توضیحات ورودی تست",
            input_type=DesignInput.InputType.TEXT,
            required=True,
            order=1
        )
        
        # ایجاد یک شرط برای تست
        self.condition = Condition.objects.create(
            section=self.section,
            title="شرط تست",
            description="توضیحات شرط تست",
            condition_type=Condition.ConditionType.CHECKBOX,
            price_modifier=100,
            order=1
        )
        
        # ایجاد ابعاد ست برای تست
        self.set_dimensions = SetDimensions.objects.create(
            title="ابعاد تست",
            width=100,
            height=100,
            price_modifier=100
        )

    def test_template_creation(self):
        """تست ایجاد قالب و ویژگی‌های آن"""
        self.assertEqual(self.template.title, "تست قالب")
        self.assertEqual(self.template.base_price, 1000)
        self.assertEqual(self.template.status, Template.Status.PUBLISHED)
        self.assertEqual(self.template.created_by, self.user)
        
    def test_section_creation(self):
        """تست ایجاد بخش و ویژگی‌های آن"""
        self.assertEqual(self.section.template, self.template)
        self.assertEqual(self.section.title, "بخش تست")
        self.assertEqual(self.section.order, 1)
        
    def test_design_input_creation(self):
        """تست ایجاد ورودی طرح و ویژگی‌های آن"""
        self.assertEqual(self.design_input.section, self.section)
        self.assertEqual(self.design_input.title, "ورودی تست")
        self.assertEqual(self.design_input.input_type, DesignInput.InputType.TEXT)
        self.assertTrue(self.design_input.required)
        
    def test_condition_creation(self):
        """تست ایجاد شرط و ویژگی‌های آن"""
        self.assertEqual(self.condition.section, self.section)
        self.assertEqual(self.condition.title, "شرط تست")
        self.assertEqual(self.condition.condition_type, Condition.ConditionType.CHECKBOX)
        self.assertEqual(self.condition.price_modifier, 100)
        
    def test_set_dimensions_creation(self):
        """تست ایجاد ابعاد ست و ویژگی‌های آن"""
        self.assertEqual(self.set_dimensions.title, "ابعاد تست")
        self.assertEqual(self.set_dimensions.width, 100)
        self.assertEqual(self.set_dimensions.height, 100)
        self.assertEqual(self.set_dimensions.price_modifier, 100)

class UserTemplateModelTests(TestCase):
    def setUp(self):
        # ایجاد یک کاربر برای تست
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # ایجاد یک قالب پایه برای تست
        self.template = Template.objects.create(
            title="تست قالب",
            description="توضیحات تست",
            base_price=1000,
            status=Template.Status.PUBLISHED,
            created_by=self.user
        )
        
        # ایجاد یک بخش برای تست
        self.section = Section.objects.create(
            template=self.template,
            title="بخش تست",
            description="توضیحات بخش تست",
            order=1
        )
        
        # ایجاد یک ورودی طرح برای تست
        self.design_input = DesignInput.objects.create(
            section=self.section,
            title="ورودی تست",
            description="توضیحات ورودی تست",
            input_type=DesignInput.InputType.TEXT,
            required=True,
            order=1
        )
        
        # ایجاد یک شرط برای تست
        self.condition = Condition.objects.create(
            section=self.section,
            title="شرط تست",
            description="توضیحات شرط تست",
            condition_type=Condition.ConditionType.CHECKBOX,
            price_modifier=100,
            order=1
        )
        
        # ایجاد قالب کاربر برای تست
        self.user_template = UserTemplate.objects.create(
            template=self.template,
            user=self.user,
            title="قالب کاربر تست",
            final_price=1000,
            status=UserTemplate.Status.DRAFT
        )
        
        # ایجاد بخش کاربر برای تست
        self.user_section = UserSection.objects.create(
            user_template=self.user_template,
            section=self.section,
            title="بخش کاربر تست"
        )
        
        # ایجاد ورودی طرح کاربر برای تست
        self.user_design_input = UserDesignInput.objects.create(
            user_section=self.user_section,
            design_input=self.design_input,
            value="مقدار تست"
        )
        
        # ایجاد شرط کاربر برای تست
        self.user_condition = UserCondition.objects.create(
            user_section=self.user_section,
            condition=self.condition,
            is_selected=True
        )

    def test_user_template_creation(self):
        """تست ایجاد قالب کاربر و ویژگی‌های آن"""
        self.assertEqual(self.user_template.template, self.template)
        self.assertEqual(self.user_template.user, self.user)
        self.assertEqual(self.user_template.title, "قالب کاربر تست")
        self.assertEqual(self.user_template.final_price, 1000)
        self.assertEqual(self.user_template.status, UserTemplate.Status.DRAFT)
        
    def test_user_section_creation(self):
        """تست ایجاد بخش کاربر و ویژگی‌های آن"""
        self.assertEqual(self.user_section.user_template, self.user_template)
        self.assertEqual(self.user_section.section, self.section)
        self.assertEqual(self.user_section.title, "بخش کاربر تست")
        
    def test_user_design_input_creation(self):
        """تست ایجاد ورودی طرح کاربر و ویژگی‌های آن"""
        self.assertEqual(self.user_design_input.user_section, self.user_section)
        self.assertEqual(self.user_design_input.design_input, self.design_input)
        self.assertEqual(self.user_design_input.value, "مقدار تست")
        
    def test_user_condition_creation(self):
        """تست ایجاد شرط کاربر و ویژگی‌های آن"""
        self.assertEqual(self.user_condition.user_section, self.user_section)
        self.assertEqual(self.user_condition.condition, self.condition)
        self.assertTrue(self.user_condition.is_selected)

class TemplateAPITests(TestCase):
    def setUp(self):
        # ایجاد یک کاربر برای تست
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # ایجاد یک کاربر ادمین برای تست
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        
        # ایجاد یک قالب پایه برای تست
        self.template = Template.objects.create(
            title="تست قالب",
            description="توضیحات تست",
            base_price=1000,
            status=Template.Status.PUBLISHED,
            created_by=self.admin_user
        )
        
        # ایجاد APIClient برای تست
        self.client = APIClient()
        
    def test_template_list_unauthenticated(self):
        """تست دسترسی به لیست قالب‌ها بدون احراز هویت"""
        url = reverse('template_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_template_create_non_admin(self):
        """تست ایجاد قالب توسط کاربر غیر ادمین (باید ناموفق باشد)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('template_list_create')
        data = {
            'title': 'قالب جدید',
            'description': 'توضیحات قالب جدید',
            'base_price': 2000,
            'status': Template.Status.DRAFT
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_template_create_admin(self):
        """تست ایجاد قالب توسط کاربر ادمین (باید موفق باشد)"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('template_list_create')
        data = {
            'title': 'قالب جدید',
            'description': 'توضیحات قالب جدید',
            'base_price': 2000,
            'status': Template.Status.DRAFT
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 2)
        
    def test_template_detail_unauthenticated(self):
        """تست دسترسی به جزئیات قالب بدون احراز هویت"""
        url = reverse('template_detail', args=[str(self.template.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'تست قالب')
        
    def test_template_update_non_admin(self):
        """تست بروزرسانی قالب توسط کاربر غیر ادمین (باید ناموفق باشد)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('template_detail', args=[str(self.template.id)])
        data = {
            'title': 'قالب به‌روز شده',
            'description': 'توضیحات به‌روز شده',
            'base_price': 3000,
            'status': Template.Status.PUBLISHED
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_template_update_admin(self):
        """تست بروزرسانی قالب توسط کاربر ادمین (باید موفق باشد)"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('template_detail', args=[str(self.template.id)])
        data = {
            'title': 'قالب به‌روز شده',
            'description': 'توضیحات به‌روز شده',
            'base_price': 3000,
            'status': Template.Status.PUBLISHED
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.template.refresh_from_db()
        self.assertEqual(self.template.title, 'قالب به‌روز شده')
        self.assertEqual(self.template.base_price, 3000)

class UserTemplateAPITests(TestCase):
    def setUp(self):
        # ایجاد یک کاربر برای تست
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # ایجاد یک کاربر دیگر برای تست
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpassword'
        )
        
        # ایجاد یک قالب پایه برای تست
        self.template = Template.objects.create(
            title="تست قالب",
            description="توضیحات تست",
            base_price=1000,
            status=Template.Status.PUBLISHED,
            created_by=self.user
        )
        
        # ایجاد یک بخش برای تست
        self.section = Section.objects.create(
            template=self.template,
            title="بخش تست",
            description="توضیحات بخش تست",
            order=1
        )
        
        # ایجاد قالب کاربر برای تست
        self.user_template = UserTemplate.objects.create(
            template=self.template,
            user=self.user,
            title="قالب کاربر تست",
            final_price=1000,
            status=UserTemplate.Status.DRAFT
        )
        
        # ایجاد بخش کاربر برای تست
        self.user_section = UserSection.objects.create(
            user_template=self.user_template,
            section=self.section,
            title="بخش کاربر تست"
        )
        
        # ایجاد APIClient برای تست
        self.client = APIClient()
        
    def test_user_template_list_authenticated(self):
        """تست دسترسی به لیست قالب‌های کاربر با احراز هویت"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user_template_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_user_template_list_unauthenticated(self):
        """تست دسترسی به لیست قالب‌های کاربر بدون احراز هویت (باید ناموفق باشد)"""
        url = reverse('user_template_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_template_create(self):
        """تست ایجاد قالب کاربر (باید موفق باشد)"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user_template_list_create')
        data = {
            'template': str(self.template.id),
            'title': 'قالب کاربر جدید',
            'status': UserTemplate.Status.DRAFT
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserTemplate.objects.count(), 2)
        
    def test_user_template_detail_owner(self):
        """تست دسترسی به جزئیات قالب کاربر توسط مالک آن"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user_template_detail', args=[str(self.user_template.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'قالب کاربر تست')
        
    def test_user_template_detail_other_user(self):
        """تست دسترسی به جزئیات قالب کاربر توسط کاربر دیگر (باید ناموفق باشد)"""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('user_template_detail', args=[str(self.user_template.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_user_template_update_owner(self):
        """تست بروزرسانی قالب کاربر توسط مالک آن"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user_template_detail', args=[str(self.user_template.id)])
        data = {
            'template': str(self.template.id),
            'title': 'قالب کاربر به‌روز شده',
            'status': UserTemplate.Status.COMPLETED
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_template.refresh_from_db()
        self.assertEqual(self.user_template.title, 'قالب کاربر به‌روز شده')
        self.assertEqual(self.user_template.status, UserTemplate.Status.COMPLETED)
        
    def test_user_template_delete_owner(self):
        """تست حذف قالب کاربر توسط مالک آن"""
        self.client.force_authenticate(user=self.user)
        url = reverse('user_template_detail', args=[str(self.user_template.id)])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(UserTemplate.objects.count(), 0)
