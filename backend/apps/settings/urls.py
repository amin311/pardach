from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    # مسیرهای API برنامه settings قرار می‌گیرند
    path('', views.settings_root, name='root'),
] 