from django.urls import path
from .views import DashboardSummaryView, DashboardStatsView, SalesDetailView, BusinessDetailView, CombinedDashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardSummaryView.as_view(), name='root'),
    path('summary/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('stats/<str:stat_type>/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('sales/', SalesDetailView.as_view(), name='sales_detail'),
    path('business/', BusinessDetailView.as_view(), name='business_detail'),
    path('combined/', CombinedDashboardView.as_view(), name='combined_dashboard'),
] 