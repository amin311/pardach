from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import ClothingSection
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from apps.core.utils import log_error

class ClothingSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClothingSection
        fields = '__all__'

class ClothingSectionListCreateView(APIView):
    """API برای دریافت لیست و ایجاد بخش‌های لباس"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست بخش‌های لباس", responses={200: ClothingSectionSerializer(many=True)})
    def get(self, request):
        """دریافت لیست بخش‌های لباس"""
        try:
            sections = ClothingSection.objects.all()
            serializer = ClothingSectionSerializer(sections, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت لیست بخش‌های لباس", e)
            return Response({'error': 'خطا در دریافت بخش‌های لباس'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد بخش لباس جدید", request=ClothingSectionSerializer, responses={201: ClothingSectionSerializer})
    def post(self, request):
        """ایجاد بخش لباس جدید"""
        try:
            # فقط ادمین‌ها می‌توانند بخش جدید ایجاد کنند
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = ClothingSectionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد بخش لباس", e)
            return Response({'error': 'خطا در ایجاد بخش لباس'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClothingSectionDetailView(APIView):
    """API برای دریافت، ویرایش و حذف بخش لباس"""
    permission_classes = [IsAuthenticated]

    def get_section(self, section_id):
        """دریافت بخش لباس"""
        try:
            return ClothingSection.objects.get(id=section_id)
        except ClothingSection.DoesNotExist:
            return None

    @extend_schema(summary="دریافت جزئیات بخش لباس", responses={200: ClothingSectionSerializer})
    def get(self, request, section_id):
        """دریافت جزئیات بخش لباس"""
        section = self.get_section(section_id)
        if not section:
            return Response({'error': 'بخش لباس یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = ClothingSectionSerializer(section)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش بخش لباس", request=ClothingSectionSerializer, responses={200: ClothingSectionSerializer})
    def put(self, request, section_id):
        """ویرایش بخش لباس"""
        if not request.user.is_staff:
            return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
        section = self.get_section(section_id)
        if not section:
            return Response({'error': 'بخش لباس یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            serializer = ClothingSectionSerializer(section, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error(f"خطا در ویرایش بخش لباس با شناسه {section_id}", e)
            return Response({'error': 'خطا در ویرایش بخش لباس'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف بخش لباس", responses={204: None})
    def delete(self, request, section_id):
        """حذف بخش لباس"""
        if not request.user.is_staff:
            return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
        section = self.get_section(section_id)
        if not section:
            return Response({'error': 'بخش لباس یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            section.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error(f"خطا در حذف بخش لباس با شناسه {section_id}", e)
            return Response({'error': 'خطا در حذف بخش لباس'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 