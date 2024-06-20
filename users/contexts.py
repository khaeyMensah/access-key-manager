from access_keys.models import AccessKey
from users.models import School
from django.db.models import Count

def common_context_data(request):
    """
    This function calculates and returns the common context data to be used across various views.

    :param request: The HTTP request object.
    :return: A dictionary containing the common context data.

    The function first calculates the total number of registered schools, the total number of active keys,
    the total number of revoked keys, and the total number of expired keys. It then creates a dictionary
    with these values and adds it to the context.

    If the user is authenticated, a school personnel, and has a school associated with their account,
    the function retrieves the user's school, the school's active key, the number of expired keys,
    the number of revoked keys, and the total number of keys purchased by the school. It then updates
    the context dictionary with these values.

    The function returns the context dictionary.
    """
    total_registered_schools = School.objects.annotate(user_count=Count('users')).filter(user_count__gt=0).count()
    total_active_keys = AccessKey.objects.filter(status='active').count()
    total_revoked_keys = AccessKey.objects.filter(status='revoked').count()
    total_expired_keys = AccessKey.objects.filter(status='expired').count()

    context = {
        'total_registered_schools': total_registered_schools,  # Note the updated context variable name
        'total_active_keys': total_active_keys,
        'total_revoked_keys': total_revoked_keys,
        'total_expired_keys': total_expired_keys,
        'total_keys_purchased': total_active_keys + total_revoked_keys + total_expired_keys,
    }

    if request.user.is_authenticated and request.user.is_school_personnel and request.user.school:
        school = request.user.school
        active_key = school.access_keys.filter(status='active').first()
        expired_keys_count = school.access_keys.filter(status='expired').count()
        revoked_keys_count = school.access_keys.filter(status='revoked').count()
        keys_purchased_count = school.access_keys.count()

        context.update({
            'active_key': active_key,
            'expired_keys_count': expired_keys_count,
            'revoked_keys_count': revoked_keys_count,
            'keys_purchased_count': keys_purchased_count,
        })

    return context

            