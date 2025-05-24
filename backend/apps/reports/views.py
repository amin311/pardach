from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from .models import Report, ReportCategory
from .serializers import ReportSerializer, ReportCategorySerializer
from .utils import (
    generate_sales_report, 
    generate_profit_report, 
    generate_user_activity_report, 
    generate_business_performance_report
)
from drf_spectacular.utils import extend_schema
from apps.core.utils import log_error, to_jalali
from django.db.models import Q
from datetime import datetime
from django.utils import timezone
from apps.notification.models import Notification
from apps.business.models import Business
from apps.authentication.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ReportCategoryListCreateView(APIView):
    """API برای دریافت لیست و ایجاد دسته‌بندی گزارش‌ها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست دسته‌بندی‌های گزارش", responses={200: ReportCategorySerializer(many=True)})
    def get(self, request):
        """دریافت لیست دسته‌بندی‌های گزارش"""
        try:
            categories = ReportCategory.objects.all()
            serializer = ReportCategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت لیست دسته‌بندی‌های گزارش", e)
            return Response({'error': 'خطا در دریافت دسته‌بندی‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد دسته‌بندی گزارش جدید", request=ReportCategorySerializer, responses={201: ReportCategorySerializer})
    def post(self, request):
        """ایجاد دسته‌بندی گزارش جدید"""
        try:
            # فقط ادمین‌ها می‌توانند دسته‌بندی جدید ایجاد کنند
            if not request.user.is_staff:
                return Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            serializer = ReportCategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد دسته‌بندی گزارش", e)
            return Response({'error': 'خطا در ایجاد دسته‌بندی'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportListCreateView(APIView):
    """API برای دریافت لیست و ایجاد گزارش‌ها"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="دریافت لیست گزارش‌ها", responses={200: ReportSerializer(many=True)})
    def get(self, request):
        """دریافت لیست گزارش‌ها"""
        try:
            # گزارش‌های متعلق به کاربر، گزارش‌های کسب‌وکارهای او و گزارش‌های عمومی
            reports = Report.objects.filter(
                Q(user=request.user) | 
                Q(business__users__user=request.user) | 
                Q(is_public=True)
            ).distinct()
            
            # فیلتر بر اساس پارامترها
            category_id = request.query_params.get('category_id')
            report_type = request.query_params.get('type')
            is_public = request.query_params.get('is_public')
            
            if category_id:
                reports = reports.filter(category_id=category_id)
            if report_type:
                reports = reports.filter(type=report_type)
            if is_public is not None:
                is_public = is_public.lower() == 'true'
                reports = reports.filter(is_public=is_public)
                
            serializer = ReportSerializer(reports, many=True)
            return Response(serializer.data)
        except Exception as e:
            log_error("خطا در دریافت لیست گزارش‌ها", e)
            return Response({'error': 'خطا در دریافت گزارش‌ها'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="ایجاد گزارش جدید", request=ReportSerializer, responses={201: ReportSerializer})
    def post(self, request):
        """ایجاد گزارش جدید"""
        try:
            serializer = ReportSerializer(data=request.data)
            if serializer.is_valid():
                report = serializer.save(user=request.user)
                
                # ارسال اعلان برای ایجاد گزارش جدید
                notification = Notification.objects.create(
                    user=request.user,
                    business=report.business,
                    type='system',
                    title=f'گزارش جدید: {report.title}',
                    content=f'گزارش {report.title} با موفقیت تولید شد.',
                    link=f'/reports/{report.id}',
                    is_read=False,
                    is_archived=False,
                    priority=2
                )
                
                # ارسال اعلان آنی با WebSocket (اگر تنظیم شده باشد)
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f'notifications_{request.user.id}',
                        {
                            'type': 'send_notification',
                            'notification': {
                                'id': str(notification.id),
                                'title': notification.title,
                                'content': notification.content,
                                'type': notification.type,
                                'is_read': notification.is_read,
                                'link': notification.link,
                                'created_at': to_jalali(notification.created_at)
                            }
                        }
                    )
                except Exception as ws_error:
                    log_error("خطا در ارسال اعلان آنی", ws_error)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error("خطا در ایجاد گزارش", e)
            return Response({'error': 'خطا در ایجاد گزارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReportDetailView(APIView):
    """API برای دریافت، ویرایش و حذف گزارش"""
    permission_classes = [IsAuthenticated]
    
    def get_report(self, report_id, user):
        """دریافت گزارش و بررسی دسترسی"""
        try:
            report = Report.objects.get(id=report_id)
            
            # بررسی دسترسی: گزارش باید متعلق به کاربر یا کسب‌وکار او باشد یا عمومی باشد
            if (report.user != user and 
                not (report.business and report.business.users.filter(user=user).exists()) and 
                not report.is_public):
                return None, Response({'error': 'دسترسی غیرمجاز'}, status=status.HTTP_403_FORBIDDEN)
                
            return report, None
        except Report.DoesNotExist:
            return None, Response({'error': 'گزارش یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            log_error(f"خطا در دریافت گزارش با شناسه {report_id}", e)
            return None, Response({'error': 'خطا در دریافت گزارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="دریافت جزئیات گزارش", responses={200: ReportSerializer})
    def get(self, request, report_id):
        """دریافت جزئیات گزارش"""
        report, error = self.get_report(report_id, request.user)
        if error:
            return error
            
        serializer = ReportSerializer(report)
        return Response(serializer.data)

    @extend_schema(summary="ویرایش گزارش", request=ReportSerializer, responses={200: ReportSerializer})
    def put(self, request, report_id):
        """ویرایش گزارش"""
        report, error = self.get_report(report_id, request.user)
        if error:
            return error
            
        # فقط مالک گزارش یا ادمین می‌تواند آن را ویرایش کند
        if report.user != request.user and not request.user.is_staff:
            return Response({'error': 'شما مجاز به ویرایش این گزارش نیستید'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            serializer = ReportSerializer(report, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_error(f"خطا در ویرایش گزارش با شناسه {report_id}", e)
            return Response({'error': 'خطا در ویرایش گزارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(summary="حذف گزارش", responses={204: None})
    def delete(self, request, report_id):
        """حذف گزارش"""
        report, error = self.get_report(report_id, request.user)
        if error:
            return error
            
        # فقط مالک گزارش یا ادمین می‌تواند آن را حذف کند
        if report.user != request.user and not request.user.is_staff:
            return Response({'error': 'شما مجاز به حذف این گزارش نیستید'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            log_error(f"خطا در حذف گزارش با شناسه {report_id}", e)
            return Response({'error': 'خطا در حذف گزارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateReportView(APIView):
    """API برای تولید گزارش‌های پویا"""
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="تولید گزارش پویا", responses={201: ReportSerializer})
    def post(self, request):
        """تولید گزارش پویا"""
        try:
            # دریافت پارامترهای ورودی
            report_type = request.data.get('type')
            business_id = request.data.get('business_id')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            category_id = request.data.get('category_id')
            is_public = request.data.get('is_public', False)
            
            if not report_type:
                return Response({'error': 'نوع گزارش الزامی است'}, status=status.HTTP_400_BAD_REQUEST)
                
            # تبدیل تاریخ‌ها
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
                end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
            except ValueError:
                return Response({'error': 'فرمت تاریخ نامعتبر است. لطفاً از قالب YYYY-MM-DD استفاده کنید'}, 
                               status=status.HTTP_400_BAD_REQUEST)
            
            # دریافت کسب‌وکار
            business = None
            if business_id:
                try:
                    business = Business.objects.get(id=business_id)
                    # بررسی دسترسی کاربر به کسب‌وکار
                    if business.owner != request.user and not business.users.filter(user=request.user).exists():
                        return Response({'error': 'شما به این کسب‌وکار دسترسی ندارید'}, 
                                      status=status.HTTP_403_FORBIDDEN)
                except Business.DoesNotExist:
                    return Response({'error': 'کسب‌وکار یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
            # تولید داده‌های گزارش بر اساس نوع
            data = None
            if report_type == 'sales':
                data = generate_sales_report(business, start_date, end_date)
            elif report_type == 'profit':
                data = generate_profit_report(business, start_date, end_date)
            elif report_type == 'user_activity':
                if not request.user.is_staff:
                    return Response({'error': 'فقط ادمین می‌تواند گزارش فعالیت کاربران را تولید کند'}, 
                                  status=status.HTTP_403_FORBIDDEN)
                data = generate_user_activity_report(start_date, end_date)
            elif report_type == 'business_performance':
                if not business:
                    return Response({'error': 'برای گزارش عملکرد کسب‌وکار، انتخاب کسب‌وکار الزامی است'}, 
                                  status=status.HTTP_400_BAD_REQUEST)
                data = generate_business_performance_report(business, start_date, end_date)
            else:
                return Response({'error': 'نوع گزارش نامعتبر است'}, status=status.HTTP_400_BAD_REQUEST)
            
            # دریافت دسته‌بندی
            category = None
            if category_id:
                try:
                    category = ReportCategory.objects.get(id=category_id)
                except ReportCategory.DoesNotExist:
                    return Response({'error': 'دسته‌بندی یافت نشد'}, status=status.HTTP_404_NOT_FOUND)
            
            # ایجاد گزارش
            date_range = ""
            if start_date and end_date:
                jalali_start = to_jalali(start_date).split()[0]
                jalali_end = to_jalali(end_date).split()[0]
                date_range = f" از {jalali_start} تا {jalali_end}"
            
            report = Report.objects.create(
                user=request.user,
                business=business,
                category=category,
                type=report_type,
                title=f"گزارش {dict(Report.TYPE_CHOICES).get(report_type, report_type)}{date_range}",
                data=data,
                is_public=is_public
            )
            
            # ارسال اعلان
            notification = Notification.objects.create(
                user=request.user,
                business=report.business,
                type='system',
                title=f'گزارش جدید: {report.title}',
                content=f'گزارش {report.title} با موفقیت تولید شد.',
                link=f'/reports/{report.id}',
                is_read=False,
                is_archived=False,
                priority=2
            )
            
            # ارسال اعلان آنی با WebSocket
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{request.user.id}',
                    {
                        'type': 'send_notification',
                        'notification': {
                            'id': str(notification.id),
                            'title': notification.title,
                            'content': notification.content,
                            'type': notification.type,
                            'is_read': notification.is_read,
                            'link': notification.link,
                            'created_at': to_jalali(notification.created_at)
                        }
                    }
                )
            except Exception as ws_error:
                log_error("خطا در ارسال اعلان آنی", ws_error)
            
            serializer = ReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            log_error("خطا در تولید گزارش", e)
            return Response({'error': 'خطا در تولید گزارش'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
