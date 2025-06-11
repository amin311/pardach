from rest_framework import serializers
from .models import Notification, NotificationCategory
from apps.core.utils import to_jalali
from django.contrib.auth import get_user_model
from apps.business.models import Business
from apps.authentication.serializers import UserSerializer
from apps.business.serializers import BusinessSerializer

User = get_user_model()

class NotificationCategorySerializer(serializers.ModelSerializer):
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = NotificationCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_created_at_jalali(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at_jalali(self, obj):
        return to_jalali(obj.updated_at)

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True, required=False)
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), source='business', required=False, allow_null=True, write_only=True)
    category = NotificationCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=NotificationCategory.objects.all(), source='category', required=False, allow_null=True, write_only=True)
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_id', 'business', 'business_id', 'category', 'category_id',
            'type', 'title', 'content', 'is_read', 'is_archived', 'link', 'priority',
            'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_created_at_jalali(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at_jalali(self, obj):
        return to_jalali(obj.updated_at) 