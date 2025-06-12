from django.urls import path
from .views import PrintCenterListCreateView, PrintCenterDetailView

urlpatterns = [
    path('', PrintCenterListCreateView.as_view(), name='print-center-list-create'),
    path('<int:pk>/', PrintCenterDetailView.as_view(), name='print-center-detail'),
]
