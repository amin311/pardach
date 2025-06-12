from django.urls import path
from .views import ClothingSectionListCreateView, ClothingSectionDetailView

app_name = 'clothing'

urlpatterns = [
    # مسیرهای مربوط به بخش‌های لباس
    path('sections/', ClothingSectionListCreateView.as_view(), name='clothing-section-list-create'),
    path('sections/<int:section_id>/', ClothingSectionDetailView.as_view(), name='clothing-section-detail'),
] 