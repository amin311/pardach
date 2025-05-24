from django.urls import path
from . import views

app_name = 'workshop'

urlpatterns = [
    # مسیرهای API برنامه workshop قرار می‌گیرند
    path('', views.workshop_root, name='workshop-root'),
] 