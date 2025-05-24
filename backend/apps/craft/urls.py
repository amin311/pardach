from django.urls import path
from . import views

app_name = 'craft'

urlpatterns = [
    # مسیرهای API برنامه craft قرار می‌گیرند
    path('', views.craft_root, name='root'),
] 