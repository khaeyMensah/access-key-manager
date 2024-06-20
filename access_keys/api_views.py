from django.contrib.auth.decorators import user_passes_test
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.helpers import is_admin
from users.models import User
from .serializers import AccessKeySerializer


from django.contrib.auth.decorators import user_passes_test, login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.models import User
from .serializers import AccessKeySerializer


@login_required
@user_passes_test(is_admin)
@api_view(['GET'])
def check_access_key_status_view(request, email):
    """
    This view checks the status of an active access key for a user associated with a school.

    Parameters:
        - request (Request): The HTTP request object.
        - email (str): The email address of the user to check the access key status for.

    Returns:
        - Response: A JSON response containing the data of the active access key if found, or an error message if not found or if the user is not associated with a school.

    Raises:
        - User.DoesNotExist: If the user with the given email address does not exist.
        - Exception: If an unexpected error occurs.

    Example:
    ```
    # Assuming the view is correctly set up and the user is authenticated and has admin privileges
    response = check_access_key_status_view(request, 'user@example.com')
    ```
    """
    if not email:
        return Response({'error': 'email parameter is required.'}, status=400)

    try:
        user = User.objects.get(email=email)
        school = user.school
        if not school:
            return Response({'error': 'User is not associated with any school.'}, status=404)

        active_key = school.access_keys.filter(status='active').first()
        if active_key:
            serializer = AccessKeySerializer(active_key)
            return Response(serializer.data, status=200)
        else:
            return Response({'error': 'No active access key found.'}, status=404)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)