from rest_framework import serializers
from .models import APIKey, APILog
from apps.core.utils import to_jalali
from apps.authentication.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class APIKeySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(write_only=True, source='user', queryset=User.objects.all(), required=False)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    last_used_at = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()

    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key', 'user', 'user_id', 'is_active',
            'expires_at', 'last_used_at', 'allowed_ips', 'rate_limit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['key']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

    def get_last_used_at(self, obj):
        return to_jalali(obj.last_used_at)

    def get_expires_at(self, obj):
        return to_jalali(obj.expires_at)

class APILogSerializer(serializers.ModelSerializer):
    api_key = APIKeySerializer(read_only=True)
    user = UserSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = APILog
        fields = [
            'id', 'api_key', 'user', 'method', 'path',
            'query_params', 'request_body', 'response_code',
            'response_body', 'ip_address', 'execution_time',
            'created_at'
        ]

    def get_created_at(self, obj):
        return to_jalali(obj.created_at) 