from django.urls import path
from .views import PrintLocationListCreateView, PrintLocationDetailView

urlpatterns = [
    path('', PrintLocationListCreateView.as_view(), name='print-location-list-create'),
    path('<int:pk>/', PrintLocationDetailView.as_view(), name='print-location-detail'),
] 