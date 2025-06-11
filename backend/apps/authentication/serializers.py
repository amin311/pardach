from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from .models import CustomUser, Role

class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل کاربر با امکان ایجاد و ویرایش"""
    password = serializers.CharField(write_only=True, required=False)
    current_role = serializers.StringRelatedField()
    roles = serializers.StringRelatedField(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        write_only=True,
        many=True,
        required=False,
        source='roles'
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'current_role', 'roles', 'role_ids', 'is_active', 'is_staff', 
                 'password', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_active', 'is_staff', 'created_at', 'updated_at']

    def create(self, validated_data):
        """ایجاد کاربر جدید با رمز عبور هش شده"""
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles', [])
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if roles:
            user.roles.set(roles)
            user.current_role = roles[0]
            user.save()
        return user

    def update(self, instance, validated_data):
        """بروزرسانی کاربر با حفظ رمز عبور در صورت عدم تغییر"""
        password = validated_data.pop('password', None)
        roles = validated_data.pop('roles', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        if roles is not None:
            instance.roles.set(roles)
            if not instance.current_role or instance.current_role not in roles:
                instance.current_role = roles[0] if roles else None
                
        instance.save()
        return instance

class RoleSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل نقش"""
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )
    permissions_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'permissions_list']
        
    def get_permissions_list(self, obj):
        """برگرداندن لیست نام‌های مجوزها"""
        return obj.get_permissions_list()

class LoginSerializer(serializers.Serializer):
    """سریالایزر برای ورود کاربر با اعتبارسنجی نام کاربری و رمز عبور"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        """اعتبارسنجی اطلاعات ورود و برگرداندن کاربر در صورت صحت"""
        user = authenticate(**data)
        if user and user.is_active:
            return {'user': user}
        raise serializers.ValidationError('نام کاربری یا رمز عبور اشتباه است') 