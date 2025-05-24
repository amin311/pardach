from rest_framework import permissions

class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    فقط کاربران ادمین می توانند تغییر دهند، اما همه می توانند ببینند.
    """
    
    def has_permission(self, request, view):
        # اجازه خواندن به همه (GET، HEAD یا OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # اجازه نوشتن فقط به ادمین‌ها
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    دسترسی فقط برای مالک آیتم یا ادمین
    """
    
    def has_object_permission(self, request, view, obj):
        # اگر کاربر ادمین یا سوپر یوزر باشد، همیشه اجازه دارد
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # بررسی مالکیت آیتم
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # در صورتی که هیچ یک از فیلدهای مالکیت وجود نداشته باشد، دسترسی ندارد
        return False 