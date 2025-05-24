from rest_framework import serializers
from .models import Tender, TenderBid
from apps.core.utils import to_jalali
from apps.business.serializers import BusinessSerializer
from apps.designs.serializers import DesignSerializer
from apps.business.models import Business
from apps.designs.models import Design

class TenderBidSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)
    business_id = serializers.PrimaryKeyRelatedField(write_only=True, source='business', queryset=Business.objects.all())
    proposed_designs = DesignSerializer(many=True, read_only=True)
    proposed_design_ids = serializers.PrimaryKeyRelatedField(
        write_only=True, source='proposed_designs', queryset=Design.objects.all(), many=True, required=False
    )
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = TenderBid
        fields = [
            'id', 'tender', 'business', 'business_id', 'proposed_price', 'description',
            'delivery_time', 'status', 'proposed_designs', 'proposed_design_ids',
            'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['tender', 'status']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

class TenderSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    winner = BusinessSerializer(read_only=True)
    winner_id = serializers.PrimaryKeyRelatedField(write_only=True, source='winner', queryset=Business.objects.all(), required=False)
    winning_bid = TenderBidSerializer(read_only=True)
    winning_bid_id = serializers.PrimaryKeyRelatedField(write_only=True, source='winning_bid', queryset=TenderBid.objects.all(), required=False)
    bids = TenderBidSerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()
    deadline_jalali = serializers.SerializerMethodField()

    class Meta:
        model = Tender
        fields = [
            'id', 'title', 'description', 'tender_type', 'created_by', 'status',
            'deadline', 'deadline_jalali', 'budget_min', 'budget_max',
            'required_design_count', 'required_print_count', 'requirements',
            'attachments', 'winner', 'winner_id', 'winning_bid', 'winning_bid_id',
            'bids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by']

    def get_created_at(self, obj):
        return to_jalali(obj.created_at)

    def get_updated_at(self, obj):
        return to_jalali(obj.updated_at)

    def get_deadline_jalali(self, obj):
        return to_jalali(obj.deadline)

    def validate(self, data):
        """اعتبارسنجی داده‌های مناقصه"""
        if 'budget_min' in data and 'budget_max' in data:
            if data['budget_min'] > data['budget_max']:
                raise serializers.ValidationError({
                    'budget_min': 'حداقل بودجه نمی‌تواند از حداکثر بودجه بیشتر باشد'
                })
        
        if 'tender_type' in data:
            if data['tender_type'] == 'design' and data.get('required_print_count', 0) > 0:
                raise serializers.ValidationError({
                    'required_print_count': 'برای مناقصه طراحی نمی‌توان تعداد چاپ تعیین کرد'
                })
            elif data['tender_type'] == 'print' and data.get('required_design_count', 0) > 0:
                raise serializers.ValidationError({
                    'required_design_count': 'برای مناقصه چاپ نمی‌توان تعداد طرح تعیین کرد'
                })
        
        return data 