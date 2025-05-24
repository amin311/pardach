from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemSettingViewSet, SiteSettingViewSet, HomeBlockViewSet,
    TenderViewSet, BidViewSet, AwardViewSet, BusinessViewSet,
    WorkshopViewSet, WorkshopTaskViewSet, WorkshopReportViewSet,
    OrderViewSet, OrderStageViewSet, TransactionViewSet,
    SetDesignViewSet
)

router = DefaultRouter()
router.register(r'system-settings', SystemSettingViewSet)
router.register(r'site-settings', SiteSettingViewSet)
router.register(r'home-blocks', HomeBlockViewSet)
router.register(r'tenders', TenderViewSet)
router.register(r'bids', BidViewSet)
router.register(r'awards', AwardViewSet)
router.register(r'businesses', BusinessViewSet)
router.register(r'workshops', WorkshopViewSet)
router.register(r'workshop-tasks', WorkshopTaskViewSet)
router.register(r'workshop-reports', WorkshopReportViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-stages', OrderStageViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'set-design', SetDesignViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 