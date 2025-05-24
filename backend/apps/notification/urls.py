from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NotificationCategoryListCreateView,
    NotificationListCreateView,
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationArchiveView,
    NotificationMarkAllReadView
)

# برای سازگاری با ViewSet (روش قبلی اپلیکیشن notifications)
router = DefaultRouter()
# اینجا می‌توانید ViewSet های خود را ثبت کنید

app_name = 'notification'

urlpatterns = [
    # مسیرهای API با روتر (برای سازگاری با کد قبلی)
    path('api/', include(router.urls)),
    
    # مسیرهای API با روش Class-Based Views
    path('categories/', NotificationCategoryListCreateView.as_view(), name='notification_category_list_create'),
    path('', NotificationListCreateView.as_view(), name='root'),
    path('<uuid:notification_id>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('<uuid:notification_id>/read/', NotificationMarkReadView.as_view(), name='notification_mark_read'),
    path('<uuid:notification_id>/archive/', NotificationArchiveView.as_view(), name='notification_archive'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification_mark_all_read'),
] 