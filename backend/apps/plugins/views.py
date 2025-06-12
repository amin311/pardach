from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import Plugin
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from apps.core.utils import log_error

class PluginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plugin
        fields = '__all__'

class PluginListCreateView(APIView):
    """API برای دریافت لیست و ایجاد افزونه‌ها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست افزونه‌ها", responses={200: PluginSerializer(many=True)})
    def get(self, request):
        """دریافت لیست افزونه‌ها"""
        try:
            plugins = Plugin.objects.all()
            # فیلتر بر اساس وضعیت فعال/غیرفعال
            active = request.query_params.get('active')
            if active is not None:
                active = active.lower() == 'true'
                plugins = plugins.filter(active=active)
                
            serializer = PluginSerializer(plugins, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت لیست افزونه‌ها", e)
            return Response({'error': 'خطا در دریافت افزونه‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد افزونه جدید", request=PluginSerializer, responses={201: PluginSerializer})
    def post(self, request):
        """ایجاد افزونه جدید"""
        try:
            # فقط ادمین‌ها می‌توانند افزونه جدید ایجاد کنند
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = PluginSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد افزونه", e)
            return Response({'error': 'خطا در ایجاد افزونه'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PluginDetailView(APIView):
    """API برای دریافت، ویرایش و حذف افزونه"""
    permission_classes = [IsAuthenticated]

    def get_plugin(self, plugin_id):
        """دریافت افزونه"""
        try:
            return Plugin.objects.get(id=plugin_id)
        except Plugin.DoesNotExist:
            return None

    @extend_schema(summary="دریافت جزئیات افزونه", responses={200: PluginSerializer})
    def get(self, request, plugin_id):
        """دریافت جزئیات افزونه"""
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return Response({'error': 'افزونه یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = PluginSerializer(plugin)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش افزونه", request=PluginSerializer, responses={200: PluginSerializer})
    def put(self, request, plugin_id):
        """ویرایش افزونه"""
        if not request.user.is_staff:
            return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return Response({'error': 'افزونه یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            serializer = PluginSerializer(plugin, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error(f"خطا در ویرایش افزونه با شناسه {plugin_id}", e)
            return Response({'error': 'خطا در ویرایش افزونه'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف افزونه", responses={204: None})
    def delete(self, request, plugin_id):
        """حذف افزونه"""
        if not request.user.is_staff:
            return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
            
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            return Response({'error': 'افزونه یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            plugin.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error(f"خطا در حذف افزونه با شناسه {plugin_id}", e)
            return Response({'error': 'خطا در حذف افزونه'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PluginToggleView(APIView):
    """API برای فعال/غیرفعال کردن افزونه"""
    permission_classes = [IsAdminUser]

    @extend_schema(summary="فعال/غیرفعال کردن افزونه", responses={200: PluginSerializer})
    def post(self, request, plugin_id):
        """فعال/غیرفعال کردن افزونه"""
        try:
            plugin = Plugin.objects.get(id=plugin_id)
        except Plugin.DoesNotExist:
            return Response({'error': 'افزونه یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
        try:
            plugin.active = not plugin.active
            plugin.save()
            
            status_text = "فعال" if plugin.active else "غیرفعال"
            return Response({
                'message': f'افزونه {plugin.name} {status_text} شد',
                'plugin': PluginSerializer(plugin).data
            })
        except Exception as e:
            log_error(f"خطا در تغییر وضعیت افزونه با شناسه {plugin_id}", e)
            return Response({'error': 'خطا در تغییر وضعیت افزونه'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 