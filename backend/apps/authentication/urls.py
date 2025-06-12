from django.urls import path
from .views import (
    RegisterView, LoginView, UserListCreateView, 
    UserDetailView, SetRoleView, RoleListCreateView, CurrentUserView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # مسیرهای مربوط به احراز هویت
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/', CurrentUserView.as_view(), name='current_user'),
    
    # مسیرهای مربوط به کاربران
    path('users/', UserListCreateView.as_view(), name='user_list_create'),
    path('users/<str:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('set-role/', SetRoleView.as_view(), name='set_role'),
    
    # مسیرهای مربوط به نقش‌ها
    path('roles/', RoleListCreateView.as_view(), name='role_list_create'),
] 