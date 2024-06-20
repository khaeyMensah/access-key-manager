from rest_framework import serializers
from .models import AccessKey


from rest_framework import serializers
from .models import AccessKey

class AccessKeySerializer(serializers.ModelSerializer):
    """
    Serializer for the AccessKey model.

    This serializer is used to convert the AccessKey model instance data
    into native Python datatypes and vice versa.

    Attributes:
        model (AccessKey): The model this serializer is based on.
        fields (list): A list of fields to include in the serialization.

    Methods:
        __init__(self, *args, **kwargs): Initializes the serializer instance.
        to_representation(self, instance): Converts an instance of the model into a dictionary.
        to_internal_value(self, data): Converts a dictionary into an instance of the model.
    """
    class Meta:
        model = AccessKey
        fields = ['key', 'status', 'procurement_date', 'expiry_date']