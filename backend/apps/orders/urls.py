from django.urls import path
from .views import (
    OrderListCreateView, 
    OrderDetailView, 
    OrderItemListCreateView,
    OrderItemDetailView
)

app_name = 'orders'

urlpatterns = [
    # مسیرهای مربوط به سفارش‌ها
    path('', OrderListCreateView.as_view(), name='order_list_create'),
    path('<uuid:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    
    # مسیرهای مربوط به آیتم‌های سفارش
    path('<uuid:order_id>/items/', OrderItemListCreateView.as_view(), name='order_item_list_create'),
    path('items/<uuid:item_id>/', OrderItemDetailView.as_view(), name='order_item_detail'),
] 