from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet,
    TransactionViewSet,
    PaymentRequestAPIView,
    PaymentVerifyAPIView,
    UserPaymentsAPIView
)

# تعریف روتر برای ViewSet ها
router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'transactions', TransactionViewSet, basename='transaction')

# الگوهای URL
urlpatterns = [
    # ViewSet ها
    path('', include(router.urls)),
    
    # پرداخت
    path('request/', PaymentRequestAPIView.as_view(), name='payment-request'),
    path('verify/', PaymentVerifyAPIView.as_view(), name='payment-verify'),
    path('user-payments/', UserPaymentsAPIView.as_view(), name='user-payments'),
] 