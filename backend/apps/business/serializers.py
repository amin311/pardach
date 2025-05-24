from rest_framework import serializers
from .models import Business, BusinessUser
from apps.core.utils import to_jalali
from apps.authentication.models import User
from apps.authentication.serializers import UserSerializer

class BusinessSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='owner', write_only=True, required=False)
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = ['id', 'name', 'slug', 'description', 'logo', 'status', 'owner', 'owner_id', 
                  'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali']
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']

    def get_created_at_jalali(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at_jalali(self, obj):
        return to_jalali(obj.updated_at)

class BusinessUserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all(), source='business', write_only=True)
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    created_at_jalali = serializers.SerializerMethodField()
    updated_at_jalali = serializers.SerializerMethodField()

    class Meta:
        model = BusinessUser
        fields = ['id', 'business', 'business_id', 'user', 'user_id', 'role', 
                  'created_at', 'updated_at', 'created_at_jalali', 'updated_at_jalali']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_created_at_jalali(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at_jalali(self, obj):
        return to_jalali(obj.updated_at) 
