from rest_framework import serializers
from .models import Chat, Message, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش اطلاعات کاربر"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class BusinessSerializer(serializers.ModelSerializer):
    """سریالایزر برای نمایش اطلاعات کسب‌وکار"""
    
    class Meta:
        model = None  # در متد __init__ تنظیم می‌شود
        fields = ['id', 'name', 'slug']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.business.models import Business
        self.Meta.model = Business

class ChatSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل چت"""
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='participants', 
        many=True, 
        write_only=True,
        required=False
    )
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(
        source='business', 
        required=False, 
        allow_null=True,
        read_only=True  # این فیلد موقتاً فقط-خواندنی است
    )
    created_at_jalali = serializers.ReadOnlyField()
    updated_at_jalali = serializers.ReadOnlyField()
    unread_messages_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id', 'title', 'participants', 'participant_ids', 
            'business', 'business_id', 'created_at', 'updated_at',
            'created_at_jalali', 'updated_at_jalali', 'unread_messages_count'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اینجا فیلد business_id را با تنظیمات جدید جایگزین می‌کنیم
        from apps.business.models import Business
        self.fields['business_id'] = serializers.PrimaryKeyRelatedField(
            queryset=Business.objects.all(),
            source='business', 
            required=False, 
            allow_null=True, 
            write_only=True
        )

    def get_unread_messages_count(self, obj):
        """محاسبه تعداد پیام‌های خوانده نشده"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0

class MessageSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل پیام"""
    sender = UserSerializer(read_only=True)
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='sender', 
        write_only=True,
        required=False
    )
    created_at_jalali = serializers.ReadOnlyField()
    updated_at_jalali = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = [
            'id', 'chat', 'sender', 'sender_id', 'content', 
            'is_read', 'created_at', 'updated_at',
            'created_at_jalali', 'updated_at_jalali'
        ]

    def create(self, validated_data):
        """ایجاد پیام جدید"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and 'sender' not in validated_data:
            validated_data['sender'] = request.user
        return super().create(validated_data)

class NotificationSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل اعلان"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='user', 
        write_only=True,
        required=False
    )
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(
        source='business', 
        required=False, 
        allow_null=True,
        read_only=True  # این فیلد موقتاً فقط-خواندنی است
    )
    created_at_jalali = serializers.ReadOnlyField()
    updated_at_jalali = serializers.ReadOnlyField()

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_id', 'business', 'business_id', 
            'type', 'title', 'content', 'is_read', 'link', 
            'created_at', 'updated_at', 'created_at_jalali', 
            'updated_at_jalali'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # اینجا فیلد business_id را با تنظیمات جدید جایگزین می‌کنیم
        from apps.business.models import Business
        self.fields['business_id'] = serializers.PrimaryKeyRelatedField(
            queryset=Business.objects.all(),
            source='business', 
            required=False, 
            allow_null=True, 
            write_only=True
        )

    def create(self, validated_data):
        """ایجاد اعلان جدید"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and 'user' not in validated_data:
            validated_data['user'] = request.user
        return super().create(validated_data) 