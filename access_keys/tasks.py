from celery import shared_task
from django.utils import timezone
from access_keys.models import AccessKey, KeyLog
from django.contrib.auth.models import User, Permission

@shared_task
def update_key_statuses():
    """
    This task updates the status of expired access keys and logs the action.

    Returns:
        str: A message indicating the completion of the task.

    Raises:
        Exception: If no admin user is found.

    Example:
    ```
    update_key_statuses.delay()
    ```
    """
    now = timezone.now().date()
    print(f"Running update_key_statuses at {now}")
    expired_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')
    system_user = User.objects.filter(is_admin=True).first()

    if not system_user:
        print('No admin user found. Please create an admin user.')
        return

    for key in expired_keys:
        key.status = 'expired'
        key.save()

        KeyLog.objects.create(
            access_key=key,
            action=f'Access key {key.key} expired for school {key.school.name}',
            user=system_user
        )
    print(f'Successfully marked {expired_keys.count()} keys as expired.')
    return "Update completed"


@shared_task
def assign_permissions():
    """
    This task assigns specific permissions to users. Grants 'can_purchase_access_key' to school personnel and 'can_revoke_access_key' to admin users.

    Returns:
        str: A message indicating the completion of the task.

    Raises:
        Exception: If a required permission does not exist.

    Example:
    ```
    assign_permissions.delay()
    ```
    """
    print("Running assign_permissions")
    try:
        school_personnel_permission = Permission.objects.get(codename='can_purchase_access_key')
        school_personnel_users = User.objects.filter(is_school_personnel=True)
        for user in school_personnel_users:
            user.user_permissions.add(school_personnel_permission)

        admin_permission = Permission.objects.get(codename='can_revoke_access_key')
        admin_users = User.objects.filter(is_admin=True)
        for user in admin_users:
            user.user_permissions.add(admin_permission)

        print('Successfully assigned permissions to users')
    except Permission.DoesNotExist:
        print('Permission does not exist')
        