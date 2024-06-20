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