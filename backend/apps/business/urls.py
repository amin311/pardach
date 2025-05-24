from django.urls import path
from .views import (
    BusinessListCreateView,
    BusinessDetailView,
    BusinessUserListCreateView,
    BusinessUserDetailView,
)

urlpatterns = [
    path('', BusinessListCreateView.as_view(), name='business-list-create'),
    path('<uuid:business_id>/', BusinessDetailView.as_view(), name='business-detail'),
    path('<uuid:business_id>/users/', BusinessUserListCreateView.as_view(), name='business-user-list-create'),
    path('<uuid:business_id>/users/<uuid:pk>/', BusinessUserDetailView.as_view(), name='business-user-detail'),
] 