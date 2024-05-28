from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import AccessKey
from .serializers import AccessKeySerializer

@api_view(['GET'])
def verify_key(request, school_email):
    try:
        access_key = AccessKey.objects.get(school__email=school_email, status='active')
        serializer = AccessKeySerializer(access_key)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AccessKey.DoesNotExist:
        return Response({'error': 'Active key not found'}, status=status.HTTP_404_NOT_FOUND)
