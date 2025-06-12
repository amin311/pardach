<<<<<<< HEAD
from apps.designs.serializers import PrintLocationSerializer

__all__ = ["PrintLocationSerializer"] 
=======
from rest_framework import serializers
from .models import PrintCenter

class PrintCenterSerializer(serializers.ModelSerializer):
    """سریالایزر برای مدل مکان چاپ"""

    class Meta:
        model = PrintCenter
        fields = [
            'id', 'name', 'address', 'city', 'phone', 'opening_hours',
            'is_active', 'latitude', 'longitude', 'contact_person', 'email'
        ]
        read_only_fields = ['id']

    def validate_phone(self, value):
        """اعتبارسنجی شماره تلفن"""
        if value and not value.replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError('شماره تلفن باید شامل ارقام باشد')
        return value

    def validate_email(self, value):
        """اعتبارسنجی ایمیل"""
        if value and '@' not in value:
            raise serializers.ValidationError('ایمیل معتبر وارد کنید')
        return value
>>>>>>> e8320ca61aa812ab6f4e88a6fdde8759cca6f772
