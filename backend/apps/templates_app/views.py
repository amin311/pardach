from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import status
from django.db.models import Q
from drf_spectacular.utils import extend_schema

from .models import Template, Section, DesignInput, Condition, UserTemplate, UserSection, UserDesignInput, UserCondition, SetDimensions
from .serializers import (
    TemplateSerializer, SectionSerializer, DesignInputSerializer, ConditionSerializer,
    UserTemplateSerializer, UserSectionSerializer, UserDesignInputSerializer, UserConditionSerializer, SetDimensionsSerializer
)
from apps.core.utils import log_error, validate_file_size, validate_file_format

# نمایش‌ها برای قالب‌ها

class TemplateListCreateView(APIView):
    """API برای نمایش لیست قالب‌ها و ایجاد قالب جدید"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست قالب‌ها", responses={200: TemplateSerializer(many=True)})
    def get(self, request):
        """دریافت لیست قالب‌ها با امکان فیلتر بر اساس دسته‌بندی، برچسب و جستجو"""
        try:
            # قالب‌های عمومی یا قالب‌های ایجاد شده توسط کاربر
            templates = Template.objects.filter(Q(is_featured=True) | Q(creator=request.user))
            
            # فیلتر بر اساس دسته‌بندی، برچسب و جستجو
            category = request.query_params.get('category')
            tag = request.query_params.get('tag')
            search = request.query_params.get('search')
            
            if category:
                templates = templates.filter(categories__id=category)
            if tag:
                templates = templates.filter(tags__id=tag)
            if search:
                templates = templates.filter(Q(title__icontains=search) | Q(description__icontains=search))
            
            serializer = TemplateSerializer(templates, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving templates", e)
            return Response({'error': 'خطا در دریافت قالب‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد قالب جدید", request=TemplateSerializer, responses={201: TemplateSerializer})
    def post(self, request):
        """ایجاد قالب جدید توسط ادمین"""
        try:
            # بررسی دسترسی ادمین
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            # اعتبارسنجی فایل تصویر
            if 'preview_image' in request.FILES:
                request.FILES['preview_image'] = validate_file_size(request.FILES['preview_image'])
                request.FILES['preview_image'] = validate_file_format(request.FILES['preview_image'])
            
            serializer = TemplateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(creator=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating template", e)
            return Response({'error': 'خطا در ایجاد قالب'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TemplateDetailView(APIView):
    """API برای نمایش، ویرایش و حذف قالب"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت جزئیات قالب", responses={200: TemplateSerializer})
    def get(self, request, template_id):
        """دریافت جزئیات قالب با شناسه مشخص"""
        try:
            template = Template.objects.get(id=template_id)
            
            # بررسی دسترسی: قالب عمومی یا ایجاد شده توسط کاربر
            if not template.is_featured and template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            # افزایش تعداد بازدید
            template.increment_view_count()
            
            serializer = TemplateSerializer(template)
            return Response(serializer.data)
        except Template.DoesNotExist:
            return Response({'error': 'قالب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving template", e)
            return Response({'error': 'خطا در دریافت قالب'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ویرایش قالب", request=TemplateSerializer, responses={200: TemplateSerializer})
    def put(self, request, template_id):
        """ویرایش قالب موجود"""
        try:
            template = Template.objects.get(id=template_id)
            
            # بررسی دسترسی: فقط سازنده یا ادمین می‌توانند ویرایش کنند
            if template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            # اعتبارسنجی فایل تصویر
            if 'preview_image' in request.FILES:
                request.FILES['preview_image'] = validate_file_size(request.FILES['preview_image'])
                request.FILES['preview_image'] = validate_file_format(request.FILES['preview_image'])
            
            serializer = TemplateSerializer(template, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Template.DoesNotExist:
            return Response({'error': 'قالب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating template", e)
            return Response({'error': 'خطا در به‌روزرسانی قالب'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف قالب", responses={204: None})
    def delete(self, request, template_id):
        """حذف قالب موجود"""
        try:
            template = Template.objects.get(id=template_id)
            
            # بررسی دسترسی: فقط سازنده یا ادمین می‌توانند حذف کنند
            if template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Template.DoesNotExist:
            return Response({'error': 'قالب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error deleting template", e)
            return Response({'error': 'خطا در حذف قالب'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# نمایش‌ها برای بخش‌ها

class SectionListCreateView(APIView):
    """API برای نمایش لیست بخش‌های یک قالب و ایجاد بخش جدید"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست بخش‌های قالب", responses={200: SectionSerializer(many=True)})
    def get(self, request, template_id):
        """دریافت لیست بخش‌های یک قالب"""
        try:
            template = Template.objects.get(id=template_id)
            
            # بررسی دسترسی: قالب عمومی یا ایجاد شده توسط کاربر
            if not template.is_featured and template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            sections = template.sections.all().order_by('order')
            serializer = SectionSerializer(sections, many=True)
            return Response(serializer.data)
        except Template.DoesNotExist:
            return Response({'error': 'قالب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving sections", e)
            return Response({'error': 'خطا در دریافت بخش‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد بخش جدید", request=SectionSerializer, responses={201: SectionSerializer})
    def post(self, request, template_id):
        """ایجاد بخش جدید برای قالب"""
        try:
            template = Template.objects.get(id=template_id)
            
            # بررسی دسترسی: فقط سازنده یا ادمین می‌توانند بخش جدید اضافه کنند
            if template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            # اعتبارسنجی فایل تصویر
            if 'preview_image' in request.FILES:
                request.FILES['preview_image'] = validate_file_size(request.FILES['preview_image'])
                request.FILES['preview_image'] = validate_file_format(request.FILES['preview_image'])
            
            data = request.data.copy()
            data['template'] = template_id
            
            serializer = SectionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Template.DoesNotExist:
            return Response({'error': 'قالب یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error creating section", e)
            return Response({'error': 'خطا در ایجاد بخش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SectionDetailView(APIView):
    """API برای نمایش، ویرایش و حذف بخش"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت جزئیات بخش", responses={200: SectionSerializer})
    def get(self, request, section_id):
        """دریافت جزئیات بخش با شناسه مشخص"""
        try:
            section = Section.objects.get(id=section_id)
            
            # بررسی دسترسی: قالب عمومی یا ایجاد شده توسط کاربر
            if not section.template.is_featured and section.template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = SectionSerializer(section)
            return Response(serializer.data)
        except Section.DoesNotExist:
            return Response({'error': 'بخش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving section", e)
            return Response({'error': 'خطا در دریافت بخش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ویرایش بخش", request=SectionSerializer, responses={200: SectionSerializer})
    def put(self, request, section_id):
        """ویرایش بخش موجود"""
        try:
            section = Section.objects.get(id=section_id)
            
            # بررسی دسترسی: فقط سازنده قالب یا ادمین می‌توانند ویرایش کنند
            if section.template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            # اعتبارسنجی فایل تصویر
            if 'preview_image' in request.FILES:
                request.FILES['preview_image'] = validate_file_size(request.FILES['preview_image'])
                request.FILES['preview_image'] = validate_file_format(request.FILES['preview_image'])
            
            serializer = SectionSerializer(section, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Section.DoesNotExist:
            return Response({'error': 'بخش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating section", e)
            return Response({'error': 'خطا در به‌روزرسانی بخش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف بخش", responses={204: None})
    def delete(self, request, section_id):
        """حذف بخش موجود"""
        try:
            section = Section.objects.get(id=section_id)
            
            # بررسی دسترسی: فقط سازنده قالب یا ادمین می‌توانند حذف کنند
            if section.template.creator != request.user and not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            section.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Section.DoesNotExist:
            return Response({'error': 'بخش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error deleting section", e)
            return Response({'error': 'خطا در حذف بخش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# نمایش‌ها برای قالب‌های کاربر

class UserTemplateListCreateView(APIView):
    """API برای نمایش لیست قالب‌های کاربر و ایجاد قالب کاربر جدید"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست قالب‌های کاربر", responses={200: UserTemplateSerializer(many=True)})
    def get(self, request):
        """دریافت لیست قالب‌های کاربر"""
        try:
            user_templates = UserTemplate.objects.filter(user=request.user)
            serializer = UserTemplateSerializer(user_templates, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving user templates", e)
            return Response({'error': 'خطا در دریافت قالب‌های کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد قالب کاربر جدید", request=UserTemplateSerializer, responses={201: UserTemplateSerializer})
    def post(self, request):
        """ایجاد قالب کاربر جدید"""
        try:
            serializer = UserTemplateSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                user_template = serializer.save()
                user_template.calculate_final_price()
                return Response(UserTemplateSerializer(user_template).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating user template", e)
            return Response({'error': 'خطا در ایجاد قالب کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserTemplateDetailView(APIView):
    """API برای نمایش، ویرایش و حذف قالب کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت جزئیات قالب کاربر", responses={200: UserTemplateSerializer})
    def get(self, request, user_template_id):
        """دریافت جزئیات قالب کاربر با شناسه مشخص"""
        try:
            user_template = UserTemplate.objects.get(id=user_template_id, user=request.user)
            serializer = UserTemplateSerializer(user_template)
            return Response(serializer.data)
        except UserTemplate.DoesNotExist:
            return Response({'error': 'قالب کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving user template", e)
            return Response({'error': 'خطا در دریافت قالب کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ویرایش قالب کاربر", request=UserTemplateSerializer, responses={200: UserTemplateSerializer})
    def put(self, request, user_template_id):
        """ویرایش قالب کاربر موجود"""
        try:
            user_template = UserTemplate.objects.get(id=user_template_id, user=request.user)
            serializer = UserTemplateSerializer(user_template, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                user_template.calculate_final_price()
                return Response(UserTemplateSerializer(user_template).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserTemplate.DoesNotExist:
            return Response({'error': 'قالب کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating user template", e)
            return Response({'error': 'خطا در به‌روزرسانی قالب کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف قالب کاربر", responses={204: None})
    def delete(self, request, user_template_id):
        """حذف قالب کاربر موجود"""
        try:
            user_template = UserTemplate.objects.get(id=user_template_id, user=request.user)
            user_template.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserTemplate.DoesNotExist:
            return Response({'error': 'قالب کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error deleting user template", e)
            return Response({'error': 'خطا در حذف قالب کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# نمایش‌ها برای بخش‌های کاربر

class UserSectionListView(APIView):
    """API برای نمایش لیست بخش‌های کاربر برای یک قالب کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست بخش‌های کاربر", responses={200: UserSectionSerializer(many=True)})
    def get(self, request, user_template_id):
        """دریافت لیست بخش‌های کاربر برای یک قالب کاربر"""
        try:
            user_template = UserTemplate.objects.get(id=user_template_id, user=request.user)
            user_sections = user_template.user_sections.all().order_by('section__order')
            serializer = UserSectionSerializer(user_sections, many=True)
            return Response(serializer.data)
        except UserTemplate.DoesNotExist:
            return Response({'error': 'قالب کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving user sections", e)
            return Response({'error': 'خطا در دریافت بخش‌های کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSectionDetailView(APIView):
    """API برای ویرایش بخش کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="ویرایش بخش کاربر", request=UserSectionSerializer, responses={200: UserSectionSerializer})
    def put(self, request, user_section_id):
        """ویرایش بخش کاربر موجود"""
        try:
            user_section = UserSection.objects.get(id=user_section_id, user_template__user=request.user)
            serializer = UserSectionSerializer(user_section, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # محاسبه مجدد قیمت نهایی قالب کاربر
                user_section.user_template.calculate_final_price()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserSection.DoesNotExist:
            return Response({'error': 'بخش کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating user section", e)
            return Response({'error': 'خطا در به‌روزرسانی بخش کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# نمایش‌ها برای ورودی‌های طرح کاربر

class UserDesignInputDetailView(APIView):
    """API برای ویرایش ورودی طرح کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="ویرایش ورودی طرح کاربر", request=UserDesignInputSerializer, responses={200: UserDesignInputSerializer})
    def put(self, request, user_design_input_id):
        """ویرایش ورودی طرح کاربر موجود"""
        try:
            user_design_input = UserDesignInput.objects.get(id=user_design_input_id, user_section__user_template__user=request.user)
            serializer = UserDesignInputSerializer(user_design_input, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # محاسبه مجدد قیمت نهایی قالب کاربر
                user_design_input.user_section.user_template.calculate_final_price()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserDesignInput.DoesNotExist:
            return Response({'error': 'ورودی طرح کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating user design input", e)
            return Response({'error': 'خطا در به‌روزرسانی ورودی طرح کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# نمایش‌ها برای شرایط کاربر

class UserConditionDetailView(APIView):
    """API برای ویرایش شرط کاربر"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="ویرایش شرط کاربر", request=UserConditionSerializer, responses={200: UserConditionSerializer})
    def put(self, request, user_condition_id):
        """ویرایش شرط کاربر موجود"""
        try:
            user_condition = UserCondition.objects.get(id=user_condition_id, user_section__user_template__user=request.user)
            serializer = UserConditionSerializer(user_condition, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                # محاسبه مجدد قیمت نهایی قالب کاربر
                user_condition.user_section.user_template.calculate_final_price()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except UserCondition.DoesNotExist:
            return Response({'error': 'شرط کاربر یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating user condition", e)
            return Response({'error': 'خطا در به‌روزرسانی شرط کاربر'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# نمایش‌ها برای ابعاد ست

class SetDimensionsListCreateView(APIView):
    """API برای نمایش لیست ابعاد ست و ایجاد ابعاد ست جدید"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست ابعاد ست", responses={200: SetDimensionsSerializer(many=True)})
    def get(self, request):
        """دریافت لیست ابعاد ست"""
        try:
            dimensions = SetDimensions.objects.all()
            serializer = SetDimensionsSerializer(dimensions, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("Error retrieving set dimensions", e)
            return Response({'error': 'خطا در دریافت ابعاد ست'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد ابعاد ست جدید", request=SetDimensionsSerializer, responses={201: SetDimensionsSerializer})
    def post(self, request):
        """ایجاد ابعاد ست جدید"""
        try:
            # بررسی دسترسی ادمین
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = SetDimensionsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("Error creating set dimensions", e)
            return Response({'error': 'خطا در ایجاد ابعاد ست'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SetDimensionsDetailView(APIView):
    """API برای نمایش، ویرایش و حذف ابعاد ست"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت جزئیات ابعاد ست", responses={200: SetDimensionsSerializer})
    def get(self, request, set_dimensions_id):
        """دریافت جزئیات ابعاد ست با شناسه مشخص"""
        try:
            dimensions = SetDimensions.objects.get(id=set_dimensions_id)
            serializer = SetDimensionsSerializer(dimensions)
            return Response(serializer.data)
        except SetDimensions.DoesNotExist:
            return Response({'error': 'ابعاد ست یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error retrieving set dimensions", e)
            return Response({'error': 'خطا در دریافت ابعاد ست'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ویرایش ابعاد ست", request=SetDimensionsSerializer, responses={200: SetDimensionsSerializer})
    def put(self, request, set_dimensions_id):
        """ویرایش ابعاد ست موجود"""
        try:
            # بررسی دسترسی ادمین
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            dimensions = SetDimensions.objects.get(id=set_dimensions_id)
            serializer = SetDimensionsSerializer(dimensions, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SetDimensions.DoesNotExist:
            return Response({'error': 'ابعاد ست یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error updating set dimensions", e)
            return Response({'error': 'خطا در به‌روزرسانی ابعاد ست'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف ابعاد ست", responses={204: None})
    def delete(self, request, set_dimensions_id):
        """حذف ابعاد ست موجود"""
        try:
            # بررسی دسترسی ادمین
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
            dimensions = SetDimensions.objects.get(id=set_dimensions_id)
            dimensions.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except SetDimensions.DoesNotExist:
            return Response({'error': 'ابعاد ست یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error("Error deleting set dimensions", e)
            return Response({'error': 'خطا در حذف ابعاد ست'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
