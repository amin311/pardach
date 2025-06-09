from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from .models import User, Role

class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل کاربر با امکان ایجاد و ویرایش"""
    password = serializers.CharField(write_only=True, required=False)
    current_role = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'current_role', 'is_active', 'is_staff', 'password', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_active', 'is_staff', 'created_at', 'updated_at']

    def create(self, validated_data):
        """ایجاد کاربر جدید با رمز عبور هش شده"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """بروزرسانی کاربر با حفظ رمز عبور در صورت عدم تغییر"""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
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