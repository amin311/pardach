from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='orderitem')
router.register(r'order-sections', views.OrderSectionViewSet, basename='ordersection')
router.register(r'order-stages', views.OrderStageViewSet, basename='orderstage')

app_name = 'orders'

urlpatterns = [
    path('', include(router.urls)),
] 