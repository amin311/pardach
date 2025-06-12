from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # مسیرهای مربوط به دسته‌بندی گزارش‌ها
    path('categories/', views.ReportCategoryListCreateView.as_view(), name='report-category-list-create'),
    
    # مسیرهای مربوط به گزارش‌ها
    path('', views.ReportListCreateView.as_view(), name='report-list-create'),
    path('<uuid:report_id>/', views.ReportDetailView.as_view(), name='report-detail'),
    
    # مسیر تولید گزارش‌های پویا
    path('generate/', views.GenerateReportView.as_view(), name='generate-report'),
] 