from rest_framework import serializers
from .models import AccessKey


class AccessKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessKey
        fields = ['key', 'status', 'procurement_date', 'expiry_date']
