from rest_framework import serializers
from .models import SetDesign
from apps.orders.serializers import OrderItemSerializer


class SetDesignSerializer(serializers.ModelSerializer):
    order_item_detail = OrderItemSerializer(source='order_item', read_only=True)
    designer_name = serializers.CharField(source='designer.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SetDesign
        fields = [
            'id', 'order_item', 'order_item_detail', 'designer', 'designer_name',
            'version', 'parent', 'file', 'preview', 'status', 'status_display',
            'price', 'paid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'version']
    
    def validate(self, data):
        # اطمینان از اینکه تغییر وضعیت طبق روال منطقی باشد
        if self.instance and 'status' in data:
            current_status = self.instance.status
            new_status = data['status']
            
            valid_transitions = {
                'waiting': ['in_progress'],
                'in_progress': ['pending_approval'],
                'pending_approval': ['completed', 'rejected'],
                'rejected': ['in_progress'],
                'completed': []  # وضعیت نهایی قابل تغییر نیست
            }
            
            if new_status not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError({
                    'status': f'تغییر وضعیت از {current_status} به {new_status} مجاز نیست'
                })
        
        return data


class SetDesignApproveSerializer(serializers.Serializer):
    approved = serializers.BooleanField(required=True)
    comment = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if not data.get('approved') and not data.get('comment'):
            raise serializers.ValidationError({
                'comment': 'در صورت رد ست‌بندی، نظر شما الزامی است'
            })
        return data


class SetDesignPaymentSerializer(serializers.Serializer):
    payment_method = serializers.CharField(required=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=0, required=True) 