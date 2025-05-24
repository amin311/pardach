from django.urls import path, include
from .views import APIKeyListCreateView, APIKeyDetailView, APILogListView

app_name = 'api'

urlpatterns = [
    # مسیرهای مدیریت کلیدهای API
    path('keys/', APIKeyListCreateView.as_view(), name='api_key_list'),
    path('keys/<uuid:key_id>/', APIKeyDetailView.as_view(), name='api_key_detail'),
    path('logs/', APILogListView.as_view(), name='api_log_list'),
    
    # مسیرهای API سایر اپ‌ها
    path('auth/', include('apps.authentication.urls')),
    path('designs/', include('apps.designs.urls')),
    path('templates/', include('apps.templates_app.urls')),
    path('orders/', include('apps.orders.urls')),
    path('business/', include('apps.business.urls')),
    path('tender/', include('apps.tender.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('reports/', include('apps.reports.urls')),
    path('settings/', include('apps.settings.urls')),
] 