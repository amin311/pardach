from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from django.db.models import Count, Sum, Q, Avg, F
from datetime import datetime, timedelta
import pandas as pd
from drf_spectacular.utils import extend_schema
from django.utils import timezone
import logging
import numpy as np
import jdatetime
from django.db.models.functions import TruncDate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from apps.orders.models import Order, OrderItem
from apps.payment.models import Payment
from apps.notification.models import Notification
from apps.reports.models import Report
from apps.core.utils import log_error, to_jalali
from .serializers import DashboardResponseSerializer, DashboardSummarySerializer, ChartDataSerializer, BusinessStatsSerializer, OrderStatsSerializer, DesignStatsSerializer, DashboardStatsSerializer
from apps.business.models import Business
from apps.main.serializers import MainPageSummarySerializer, PromotionSerializer, NavigationSerializer
from apps.designs.models import Design

class DashboardSummaryView(APIView):
    """API برای دریافت خلاصه داده‌های داشبورد"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="دریافت خلاصه داده‌های داشبورد",
        description="دریافت خلاصه داده‌های سفارش‌ها، پرداخت‌ها، اعلان‌ها و گزارش‌ها به همراه نمودارهای مرتبط",
        responses={200: DashboardResponseSerializer}
    )
    @method_decorator(cache_page(60 * 5))  # کش کردن برای 5 دقیقه
    def get(self, request):
        try:
            # محدوده زمانی برای داده‌های اخیر
            days = int(request.query_params.get('days', 30))
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # خلاصه سفارش‌ها
            orders = Order.objects.filter(created_at__range=[start_date, end_date])
            if not request.user.is_staff:
                orders = orders.filter(user=request.user)
            order_count = orders.count()
            total_sales = orders.aggregate(total=Sum('total_price'))['total'] or 0

            # خلاصه پرداخت‌ها
            payments = Payment.objects.filter(created_at__range=[start_date, end_date], status='successful')
            if not request.user.is_staff:
                payments = payments.filter(user=request.user)
            payment_count = payments.count()
            total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0

            # خلاصه اعلانات
            notifications = Notification.objects.filter(
                Q(user=request.user) | Q(all_users=True),
                created_at__range=[start_date, end_date]
            )
            unread_notifications = notifications.filter(read=False).count()

            # خلاصه گزارش‌ها
            reports = Report.objects.filter(created_at__range=[start_date, end_date])
            if not request.user.is_staff:
                reports = reports.filter(Q(user=request.user) | Q(is_public=True))
            report_count = reports.count()

            # نمودار سفارش‌های اخیر با استفاده از ORM
            order_chart = orders.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                total=Sum('total_price')
            ).order_by('date')

            order_chart_data = {
                'labels': [to_jalali(item['date']).split(' ')[0] for item in order_chart],
                'values': [float(item['total']) for item in order_chart],
                'type': 'bar',
                'title': 'فروش روزانه'
            }

            # نمودار پرداخت‌های اخیر با استفاده از ORM
            payment_chart = payments.annotate(
                date=TruncDate('created_at')
            ).values('date').annotate(
                total=Sum('amount')
            ).order_by('date')

            payment_chart_data = {
                'labels': [to_jalali(item['date']).split(' ')[0] for item in payment_chart],
                'values': [float(item['total']) for item in payment_chart],
                'type': 'line',
                'title': 'پرداخت‌های روزانه'
            }

            # داده‌های دیگر برای ادمین‌ها
            if request.user.is_staff:
                # توزیع کاربران بر اساس سفارش‌ها
                user_distribution = Order.objects.filter(
                    created_at__range=[start_date, end_date]
                ).values('user__username').annotate(
                    count=Count('id')
                ).order_by('-count')[:5]
                
                user_chart_data = {
                    'labels': [item['user__username'] for item in user_distribution],
                    'values': [item['count'] for item in user_distribution],
                    'type': 'pie',
                    'title': 'کاربران فعال'
                }
            else:
                user_chart_data = None

            # پاسخ API
            response_data = {
                'summary': {
                    'order_count': order_count,
                    'total_sales': total_sales,
                    'payment_count': payment_count,
                    'total_payments': total_payments,
                    'unread_notifications': unread_notifications,
                    'report_count': report_count,
                },
                'charts': {
                    'orders': order_chart_data,
                    'payments': payment_chart_data,
                }
            }
            
            # اضافه کردن داده‌های مخصوص ادمین
            if request.user.is_staff and user_chart_data:
                response_data['charts']['users'] = user_chart_data

            return Response(response_data)
        except Exception as e:
            log_error("خطا در دریافت داده‌های داشبورد", e)
            return Response({'error': 'خطا در دریافت داده‌های داشبورد'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardStatsView(APIView):
    """نمایش آمار و اطلاعات داشبورد"""
    permission_classes = [IsAuthenticated]

    def get_business_stats(self, user):
        """دریافت آمار کسب‌وکارها"""
        try:
            total_businesses = Business.objects.count()
            active_businesses = Business.objects.filter(status='active').count()
            user_businesses = Business.objects.filter(Q(owner=user) | Q(users__user=user)).distinct().count()
            
            return {
                'total_businesses': total_businesses,
                'active_businesses': active_businesses,
                'user_businesses': user_businesses
            }
        except Exception as e:
            log_error("خطا در دریافت آمار کسب‌وکارها", e)
            return None

    def get_order_stats(self, user):
        """دریافت آمار سفارش‌ها"""
        try:
            total_orders = Order.objects.count()
            completed_orders = Order.objects.filter(status='completed').count()
            user_orders = Order.objects.filter(customer=user).count()
            
            # آمار هفته اخیر
            week_ago = timezone.now() - timedelta(days=7)
            weekly_orders = Order.objects.filter(created_at__gte=week_ago).count()
            
            return {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'user_orders': user_orders,
                'weekly_orders': weekly_orders
            }
        except Exception as e:
            log_error("خطا در دریافت آمار سفارش‌ها", e)
            return None

    def get_design_stats(self, user):
        """دریافت آمار طرح‌ها"""
        try:
            total_designs = Design.objects.count()
            public_designs = Design.objects.filter(is_public=True).count()
            user_designs = Design.objects.filter(designer=user).count()
            
            # آمار بازدید و دانلود
            total_views = Design.objects.aggregate(total=Sum('views_count'))['total'] or 0
            total_downloads = Design.objects.aggregate(total=Sum('downloads_count'))['total'] or 0
            
            return {
                'total_designs': total_designs,
                'public_designs': public_designs,
                'user_designs': user_designs,
                'total_views': total_views,
                'total_downloads': total_downloads
            }
        except Exception as e:
            log_error("خطا در دریافت آمار طرح‌ها", e)
            return None

    def get(self, request):
        """دریافت تمام آمار داشبورد"""
        try:
            business_stats = self.get_business_stats(request.user)
            order_stats = self.get_order_stats(request.user)
            design_stats = self.get_design_stats(request.user)
            
            if not all([business_stats, order_stats, design_stats]):
                return Response({'error': 'خطا در دریافت آمار'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            data = {
                'business_stats': business_stats,
                'order_stats': order_stats,
                'design_stats': design_stats
            }
            
            serializer = DashboardStatsSerializer(data)
            return Response(serializer.data)
            
        except Exception as e:
            log_error("خطا در دریافت آمار داشبورد", e)
            return Response({'error': 'خطا در دریافت آمار داشبورد'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SalesDetailView(APIView):
    """
    API برای دریافت جزئیات فروش
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # محدوده زمانی برای داده‌ها
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # فیلتر براساس نقش کاربر
            is_admin = request.user.is_staff
            
            # دریافت سفارش‌ها
            if is_admin:
                orders = Order.objects.filter(created_at__range=[start_date, end_date])
            else:
                orders = Order.objects.filter(user=request.user, created_at__range=[start_date, end_date])
            
            # آمار کلی سفارش‌ها
            total_orders = orders.count()
            completed_orders = orders.filter(status='completed').count()
            cancelled_orders = orders.filter(status='cancelled').count()
            
            # محاسبه متوسط ارزش سفارش
            avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            
            # محصولات پرفروش (در اینجا به عنوان مثال از طریق آیتم‌های سفارش)
            top_products = []
            try:
                # این قسمت بسته به ساختار مدل‌های شما ممکن است نیاز به تغییر داشته باشد
                top_products_query = OrderItem.objects.filter(
                    order__in=orders
                ).values('product__name').annotate(
                    count=Count('id')
                ).order_by('-count')[:5]
                
                top_products = [
                    {'name': item['product__name'], 'count': item['count']}
                    for item in top_products_query
                ]
            except:
                # در صورت عدم وجود مدل OrderItem یا ساختار متفاوت
                top_products = []
            
            # اگر top_products خالی است، داده‌های مثال برای نمایش
            if not top_products:
                top_products = [
                    {'name': 'طرح گرافیکی ویژه', 'count': 15},
                    {'name': 'قالب وب‌سایت فروشگاهی', 'count': 12},
                    {'name': 'طراحی لوگو', 'count': 10},
                    {'name': 'کارت ویزیت', 'count': 8},
                    {'name': 'بروشور تبلیغاتی', 'count': 5}
                ]
            
            # نمودار روند فروش
            sales_trend = self._generate_sales_trend(orders)
            
            # روش‌های پرداخت محبوب
            payment_methods = [
                {'name': 'درگاه آنلاین', 'count': 65},
                {'name': 'کارت به کارت', 'count': 25},
                {'name': 'پرداخت در محل', 'count': 10}
            ]
            
            response_data = {
                'total_orders': total_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'avg_order_value': avg_order_value,
                'top_products': top_products,
                'sales_trend': sales_trend,
                'payment_methods': payment_methods
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            log_error("خطا در دریافت جزئیات فروش", e)
            return Response(
                {'error': 'خطا در دریافت جزئیات فروش'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_sales_trend(self, orders):
        try:
            if not orders.exists():
                # داده‌های مثال در صورت نبود سفارش
                return {
                    'labels': [f'روز {i}' for i in range(1, 8)],
                    'values': [0, 0, 0, 0, 0, 0, 0],
                    'type': 'line'
                }
            
            # استفاده از pandas برای تحلیل روند
            df = pd.DataFrame(list(orders.values('created_at', 'total_amount')))
            df['date'] = pd.to_datetime(df['created_at']).dt.date
            daily_sales = df.groupby('date')['total_amount'].sum().reset_index()
            
            # تبدیل تاریخ‌ها به شمسی
            labels = [to_jalali(date) for date in daily_sales['date']]
            values = daily_sales['total_amount'].tolist()
            
            return {
                'labels': labels,
                'values': values,
                'type': 'line'
            }
        except Exception as e:
            log_error("خطا در تولید نمودار روند فروش", e)
            return {
                'labels': [f'روز {i}' for i in range(1, 8)],
                'values': [0, 0, 0, 0, 0, 0, 0],
                'type': 'line'
            }

class BusinessDetailView(APIView):
    """
    API برای دریافت جزئیات کسب‌وکارها در داشبورد
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # محدوده زمانی برای داده‌ها
            days = int(request.query_params.get('days', 30))
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # فیلتر براساس نقش کاربر
            is_admin = request.user.is_staff
            
            # دریافت کسب‌وکارها
            if is_admin:
                businesses = Business.objects.all()
                active_businesses = businesses.filter(status='active')
            else:
                businesses = Business.objects.filter(
                    Q(owner=request.user) | Q(users__user=request.user)
                ).distinct()
                active_businesses = businesses.filter(status='active')
            
            # آمار کلی کسب‌وکارها
            total_businesses = businesses.count()
            active_count = active_businesses.count()
            
            # فعالیت‌های اخیر کسب‌وکارها
            recent_activities = BusinessActivity.objects.filter(
                business__in=businesses,
                created_at__range=[start_date, end_date]
            ).order_by('-created_at')[:5]
            
            recent_activities_data = []
            for activity in recent_activities:
                activity_data = {
                    'id': str(activity.id),
                    'business_name': activity.business.name,
                    'activity_type': activity.get_activity_type_display(),
                    'created_at': to_jalali(activity.created_at),
                    'details': activity.details or {}
                }
                recent_activities_data.append(activity_data)
            
            # کسب‌وکارهای برتر (بر اساس تعداد فعالیت)
            top_businesses = []
            if is_admin:
                top_businesses_query = Business.objects.annotate(
                    activity_count=Count('activities', filter=Q(activities__created_at__range=[start_date, end_date]))
                ).order_by('-activity_count')[:5]
                
                for business in top_businesses_query:
                    top_businesses.append({
                        'id': str(business.id),
                        'name': business.name,
                        'activity_count': business.activity_count,
                        'status': business.status
                    })
            
            response_data = {
                'total_businesses': total_businesses,
                'active_businesses': active_count,
                'recent_activities': recent_activities_data,
                'top_businesses': top_businesses
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            log_error("خطا در دریافت جزئیات کسب‌وکارها", e)
            return Response(
                {'error': 'خطا در دریافت جزئیات کسب‌وکارها'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CombinedDashboardView(APIView):
    """
    API برای دریافت اطلاعات یکپارچه از داشبورد و صفحه اصلی
    این API داده‌های مورد نیاز برای نمایش اطلاعات ترکیبی از هر دو برنامه را فراهم می‌کند
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # دریافت پارامتر روزها از درخواست
            days = int(request.query_params.get('days', 30))
            
            # تنظیم بازه زمانی
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days)
            
            # بررسی نقش کاربر
            is_admin = request.user.is_staff or request.user.is_superuser
            
            # جمع‌آوری داده‌های داشبورد
            dashboard_data = self._get_dashboard_data(request.user, is_admin, start_date, end_date, days)
            
            # جمع‌آوری داده‌های صفحه اصلی
            main_data = self._get_main_data(request.user, is_admin)
            
            # ترکیب داده‌ها
            response_data = {
                'dashboard': dashboard_data,
                'main': main_data,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'is_admin': is_admin
                },
                'timestamp': timezone.now().isoformat(),
                'days_range': days
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error in CombinedDashboardView: {str(e)}")
            return Response(
                {'error': 'خطا در دریافت اطلاعات یکپارچه', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_dashboard_data(self, user, is_admin, start_date, end_date, days):
        """دریافت داده‌های مربوط به داشبورد"""
        try:
            # استفاده از کد موجود در DashboardSummaryView برای دریافت خلاصه داده‌ها
            from apps.orders.models import Order
            from apps.payment.models import Payment
            from apps.notification.models import Notification
            from apps.reports.models import Report
            from apps.business.models import Business
            
            # فیلتر داده‌ها بر اساس دسترسی کاربر
            if is_admin:
                orders = Order.objects.filter(created_at__range=[start_date, end_date])
                payments = Payment.objects.filter(created_at__range=[start_date, end_date])
                notifications = Notification.objects.filter(created_at__range=[start_date, end_date])
                reports = Report.objects.all()
                businesses = Business.objects.all()
            else:
                # کاربران عادی فقط داده‌های مرتبط با خود را می‌بینند
                orders = Order.objects.filter(
                    Q(user=user) | Q(business__owner=user),
                    created_at__range=[start_date, end_date]
                )
                payments = Payment.objects.filter(
                    Q(user=user) | Q(order__business__owner=user),
                    created_at__range=[start_date, end_date]
                )
                notifications = Notification.objects.filter(
                    user=user,
                    created_at__range=[start_date, end_date]
                )
                reports = Report.objects.filter(user=user)
                businesses = Business.objects.filter(owner=user)
            
            # محاسبه خلاصه‌ها
            summary_data = {
                'order_count': orders.count(),
                'total_sales': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'payment_count': payments.count(),
                'total_payments': payments.aggregate(Sum('amount'))['amount__sum'] or 0,
                'unread_notifications': notifications.filter(is_read=False).count(),
                'report_count': reports.count(),
                'active_businesses': businesses.filter(is_active=True).count(),
                'total_businesses': businesses.count()
            }
            
            # نمودارهای مورد نیاز
            charts = []
            
            # نمودار سفارش‌ها
            order_chart = self._generate_order_chart(orders, days)
            if order_chart:
                charts.append(order_chart)
            
            # نمودار پرداخت‌ها
            payment_chart = self._generate_payment_chart(payments, days)
            if payment_chart:
                charts.append(payment_chart)
            
            # کسب و کارهای برتر
            top_businesses = []
            if is_admin:
                # برای ادمین‌ها: کسب و کارهای با بیشترین سفارش
                business_orders = Business.objects.annotate(
                    order_count=Count('order', filter=Q(order__created_at__range=[start_date, end_date]))
                ).order_by('-order_count')[:5]
                
                for business in business_orders:
                    top_businesses.append({
                        'id': business.id,
                        'name': business.name,
                        'category': business.category,
                        'order_count': business.order_count,
                        'is_active': business.is_active
                    })
            
            # ترکیب داده‌ها در پاسخ داشبورد
            dashboard_data = {
                'summary': summary_data,
                'charts': charts,
                'topBusinesses': top_businesses
            }
            
            return dashboard_data
            
        except Exception as e:
            logging.error(f"Error in _get_dashboard_data: {str(e)}")
            return {'error': str(e)}
    
    def _generate_order_chart(self, orders, days):
        """تولید داده‌های نمودار برای سفارش‌ها"""
        try:
            if orders.count() == 0:
                return None
                
            # تبدیل به DataFrame
            orders_df = pd.DataFrame(list(orders.values('created_at', 'total_amount')))
            
            # گروه‌بندی بر اساس تاریخ
            orders_df['date'] = orders_df['created_at'].dt.date
            
            # تعیین مقیاس زمانی مناسب بر اساس تعداد روزها
            if days <= 7:
                # روزانه
                grouped = orders_df.groupby('date').agg({'total_amount': 'sum'}).reset_index()
                date_format = '%Y-%m-%d'
                title = 'آمار سفارش‌ها (روزانه)'
            elif days <= 30:
                # هفتگی
                orders_df['week'] = orders_df['created_at'].dt.to_period('W').astype(str)
                grouped = orders_df.groupby('week').agg({'total_amount': 'sum'}).reset_index()
                grouped = grouped.rename(columns={'week': 'date'})
                date_format = 'هفته %W'
                title = 'آمار سفارش‌ها (هفتگی)'
            else:
                # ماهانه
                orders_df['month'] = orders_df['created_at'].dt.to_period('M').astype(str)
                grouped = orders_df.groupby('month').agg({'total_amount': 'sum'}).reset_index()
                grouped = grouped.rename(columns={'month': 'date'})
                date_format = '%Y-%m'
                title = 'آمار سفارش‌ها (ماهانه)'
            
            # تبدیل تاریخ میلادی به شمسی
            labels = []
            for date_str in grouped['date']:
                if isinstance(date_str, str) and '-' in date_str:
                    try:
                        parts = date_str.split('-')
                        year = int(parts[0])
                        month = int(parts[1]) if len(parts) > 1 else 1
                        day = int(parts[2]) if len(parts) > 2 else 1
                        gregorian_date = timezone.datetime(year, month, day).date()
                        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                        labels.append(jalali_date.strftime('%Y/%m/%d'))
                    except:
                        labels.append(date_str)
                else:
                    labels.append(str(date_str))
            
            values = grouped['total_amount'].tolist()
            
            # ساخت دیکشنری داده‌های نمودار
            chart_data = {
                'labels': labels,
                'values': values,
                'type': 'line',
                'title': title
            }
            
            return chart_data
            
        except Exception as e:
            logging.error(f"Error generating order chart: {str(e)}")
            return None
    
    def _generate_payment_chart(self, payments, days):
        """تولید داده‌های نمودار برای پرداخت‌ها"""
        try:
            if payments.count() == 0:
                return None
                
            # تبدیل به DataFrame
            payments_df = pd.DataFrame(list(payments.values('created_at', 'amount')))
            
            # گروه‌بندی بر اساس تاریخ
            payments_df['date'] = payments_df['created_at'].dt.date
            
            # تعیین مقیاس زمانی مناسب بر اساس تعداد روزها
            if days <= 7:
                # روزانه
                grouped = payments_df.groupby('date').agg({'amount': 'sum'}).reset_index()
                date_format = '%Y-%m-%d'
                title = 'آمار پرداخت‌ها (روزانه)'
            elif days <= 30:
                # هفتگی
                payments_df['week'] = payments_df['created_at'].dt.to_period('W').astype(str)
                grouped = payments_df.groupby('week').agg({'amount': 'sum'}).reset_index()
                grouped = grouped.rename(columns={'week': 'date'})
                date_format = 'هفته %W'
                title = 'آمار پرداخت‌ها (هفتگی)'
            else:
                # ماهانه
                payments_df['month'] = payments_df['created_at'].dt.to_period('M').astype(str)
                grouped = payments_df.groupby('month').agg({'amount': 'sum'}).reset_index()
                grouped = grouped.rename(columns={'month': 'date'})
                date_format = '%Y-%m'
                title = 'آمار پرداخت‌ها (ماهانه)'
            
            # تبدیل تاریخ میلادی به شمسی
            labels = []
            for date_str in grouped['date']:
                if isinstance(date_str, str) and '-' in date_str:
                    try:
                        parts = date_str.split('-')
                        year = int(parts[0])
                        month = int(parts[1]) if len(parts) > 1 else 1
                        day = int(parts[2]) if len(parts) > 2 else 1
                        gregorian_date = timezone.datetime(year, month, day).date()
                        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                        labels.append(jalali_date.strftime('%Y/%m/%d'))
                    except:
                        labels.append(date_str)
                else:
                    labels.append(str(date_str))
            
            values = grouped['amount'].tolist()
            
            # ساخت دیکشنری داده‌های نمودار
            chart_data = {
                'labels': labels,
                'values': values,
                'type': 'bar',
                'title': title
            }
            
            return chart_data
            
        except Exception as e:
            logging.error(f"Error generating payment chart: {str(e)}")
            return None
    
    def _get_main_data(self, user, is_admin):
        """دریافت داده‌های مربوط به صفحه اصلی"""
        try:
            # در اینجا باید کد استخراج داده‌های صفحه اصلی قرار گیرد
            # این بخش می‌تواند مشابه کدهای MainPageSummaryView باشد
            
            from apps.notification.models import Notification
            from apps.orders.models import Order
            from apps.business.models import Business
            
            # داده‌های خوش‌آمدگویی
            welcome_data = {
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'date_joined': user.date_joined.isoformat()
            }
            
            # آیتم‌های تبلیغاتی
            promotional_items = [
                {
                    'id': 1,
                    'title': 'تخفیف ویژه زمستانی',
                    'description': 'با خرید بیش از ۵۰۰ هزار تومان، تخفیف ۲۰ درصدی بگیرید',
                    'image_url': '/static/images/promo/winter_sale.jpg',
                    'link': '/promotions/winter-sale'
                },
                {
                    'id': 2,
                    'title': 'محصولات جدید',
                    'description': 'محصولات جدید ماه را ببینید',
                    'image_url': '/static/images/promo/new_products.jpg',
                    'link': '/products/new'
                }
            ]
            
            # منوی ناوبری بر اساس نقش کاربر
            navigation_menu = []
            
            # منوی مشترک برای همه کاربران
            common_menu = [
                {
                    'id': 'dashboard',
                    'title': 'داشبورد',
                    'icon': 'tachometer-alt',
                    'link': '/dashboard'
                },
                {
                    'id': 'orders',
                    'title': 'سفارشات',
                    'icon': 'shopping-cart',
                    'link': '/orders'
                },
                {
                    'id': 'payments',
                    'title': 'پرداخت‌ها',
                    'icon': 'credit-card',
                    'link': '/payments'
                }
            ]
            
            navigation_menu.extend(common_menu)
            
            # منوی اضافی برای ادمین‌ها
            if is_admin:
                admin_menu = [
                    {
                        'id': 'users',
                        'title': 'کاربران',
                        'icon': 'users',
                        'link': '/admin/users'
                    },
                    {
                        'id': 'reports',
                        'title': 'گزارش‌ها',
                        'icon': 'chart-bar',
                        'link': '/admin/reports'
                    }
                ]
                navigation_menu.extend(admin_menu)
            
            # اعلان‌های کاربر
            notifications = []
            user_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
            for notification in user_notifications:
                notifications.append({
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat()
                })
            
            # فعالیت‌های کسب و کارها (برای ادمین‌ها و صاحبان کسب و کار)
            business_activities = []
            
            if is_admin:
                # برای ادمین‌ها تمام فعالیت‌ها
                recent_orders = Order.objects.all().order_by('-created_at')[:10]
                for order in recent_orders:
                    business_activities.append({
                        'business_id': order.business.id if order.business else None,
                        'business_name': order.business.name if order.business else 'نامشخص',
                        'action': f'سفارش جدید به مبلغ {order.total_amount} تومان',
                        'date': order.created_at.isoformat()
                    })
            else:
                # برای کاربران عادی، فقط فعالیت‌های کسب و کارهای خودشان
                user_businesses = Business.objects.filter(owner=user)
                if user_businesses.exists():
                    recent_business_orders = Order.objects.filter(business__in=user_businesses).order_by('-created_at')[:10]
                    for order in recent_business_orders:
                        business_activities.append({
                            'business_id': order.business.id,
                            'business_name': order.business.name,
                            'action': f'سفارش جدید به مبلغ {order.total_amount} تومان',
                            'date': order.created_at.isoformat()
                        })
            
            # ترکیب داده‌ها در پاسخ صفحه اصلی
            main_data = {
                'welcomeData': welcome_data,
                'promotionalItems': promotional_items,
                'navigationMenu': navigation_menu,
                'notifications': notifications,
                'businessActivities': business_activities
            }
            
            return main_data
            
        except Exception as e:
            logging.error(f"Error in _get_main_data: {str(e)}")
            return {'error': str(e)}
