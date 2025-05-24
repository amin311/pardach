from django.urls import path
from .views import MainPageSummaryView, MainSummaryView, PromotionListView, PromotionDetailView, MainSettingView, home

app_name = 'main'

urlpatterns = [
    path('', home, name='home'),
    path('page-summary/', MainPageSummaryView.as_view(), name='main_page_summary'),
    path('summary/', MainSummaryView.as_view(), name='main_summary'),
    path('promotions/', PromotionListView.as_view(), name='promotion_list'),
    path('promotions/<int:pk>/', PromotionDetailView.as_view(), name='promotion_detail'),
    path('settings/', MainSettingView.as_view(), name='main_settings'),
] 