import logging
from django.contrib.auth.decorators import user_passes_test, login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view
from users.helpers import is_admin
from users.models import User
from .serializers import AccessKeySerializer


logger = logging.getLogger(__name__)

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
    """
    logger.info(f"Checking access key status for email: {email}")

    if not email:
        logger.error('Email parameter is required.')
        return Response({'error': 'Email parameter is required.'}, status=400)

    try:
        user = User.objects.get(email=email)
        school = user.school
        if not school:
            logger.warning(f'User with email {email} is not associated with any school.')
            return Response({'error': 'User is not associated with any school.'}, status=404)

        active_key = school.access_keys.filter(status='active').first()
        if active_key:
            serializer = AccessKeySerializer(active_key)
            logger.info(f'Active access key found for email {email}.')
            return Response(serializer.data, status=200)
        else:
            logger.info(f'No active access key found for email {email}.')
            return Response({'error': 'No active access key found.'}, status=404)
    except User.DoesNotExist:
        logger.error(f'User with email {email} not found.')
        return Response({'error': 'User not found.'}, status=404)
    except Exception as e:
        logger.exception(f'Error checking access key status for email {email}: {str(e)}')
        return Response({'error': str(e)}, status=500)
