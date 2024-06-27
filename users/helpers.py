from django.core.exceptions import PermissionDenied
from functools import wraps

def is_school_personnel(user):
    """
    Checks if the user is a school personnel.

    Args:
        user (User): The user object to be checked.

    Returns:
        bool: True if the user is a school personnel, False otherwise.

    Raises:
        AttributeError: If the user object does not have 'is_authenticated' or 'is_school_personnel' attributes.
    """
    return user.is_authenticated and user.is_school_personnel


def is_admin(user):
    """
    Checks if the given user is an admin.

    Args:
        user (User): The user object to be checked.

    Returns:
        bool: True if the user is an admin, False otherwise.

    Raises:
        AttributeError: If the user object does not have 'is_authenticated' or 'is_admin' attributes.
    """
    return user.is_authenticated and user.is_admin


def user_passes_test_with_403(test_func):
    """
    Decorator for views that checks whether the user passes the given test,
    and if not, raises a PermissionDenied response.

    Args:
        test_func (function): A function that takes a User object and returns a boolean.

    Returns:
        A decorator that takes a view function as an argument.

    Raises:
        PermissionDenied: If the user does not pass the test.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not test_func(request.user):
                raise PermissionDenied("You don't have permission to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


