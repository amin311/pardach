from rest_framework import serializers
from .models import Report, ReportCategory
from apps.core.utils import to_jalali
from apps.authentication.serializers import UserSerializer
from apps.business.serializers import BusinessSerializer
from django.contrib.auth import get_user_model
from apps.business.models import Business

User = get_user_model()

class ReportCategorySerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل ReportCategory"""
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = ReportCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_created_at_jalali(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at_jalali(self, obj):
        return to_jalali(obj.updated_at)

class ReportSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل Report"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True, required=False)
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), source='business', required=False, allow_null=True, write_only=True)
    category = ReportCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=ReportCategory.objects.all(), source='category', required=False, allow_null=True, write_only=True)
    generated_at_jalali = serializers.SerializerMethodField()
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            'id', 'user', 'user_id', 'business', 'business_id', 'category', 'category_id',
            'type', 'title', 'data', 'is_public', 'generated_at', 'generated_at_jalali',
            'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali'
        ]
        read_only_fields = ['id', 'generated_at', 'created_at', 'updated_at']

    def get_generated_at_jalali(self, obj):
        return to_jalali(obj.generated_at)

    def get_created_at_jalali(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at_jalali(self, obj):
        return to_jalali(obj.updated_at) 