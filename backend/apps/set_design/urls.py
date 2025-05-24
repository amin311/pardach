from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SetDesignViewSet

router = DefaultRouter()
router.register(r'set-design', SetDesignViewSet, basename='set-design')

urlpatterns = [
    path('', include(router.urls)),
] 