from django.urls import path
from .views import (
    TenderListCreateView, TenderDetailView,
    TenderBidListCreateView, TenderBidDetailView
)

app_name = 'tender'

urlpatterns = [
    path('', TenderListCreateView.as_view(), name='tender_list'),
    path('<uuid:tender_id>/', TenderDetailView.as_view(), name='tender_detail'),
    path('<uuid:tender_id>/bids/', TenderBidListCreateView.as_view(), name='tender_bid_list'),
    path('<uuid:tender_id>/bids/<uuid:bid_id>/', TenderBidDetailView.as_view(), name='tender_bid_detail'),
] 