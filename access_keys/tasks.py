from celery import shared_task
from django.utils import timezone
from access_keys.models import AccessKey, KeyLog
from users.models import User 

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
    print(f"Running update_key_statuses at {now}")  # Confirm task execution
    expired_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')
    print(f"Found {expired_keys.count()} expired keys")  # Confirm number of keys to be processed

    system_user = User.objects.filter(is_superuser=True).first()

    if not system_user:
        print('No admin user found. Please create an admin user.')
        return

    for key in expired_keys:
        key.status = 'expired'
        key.save()
        print(f"Expired key: {key.key}")  # Confirm key expiry

        KeyLog.objects.create(
            access_key=key,
            action=f'Access key {key.key} expired for school {key.school.name}',
            user=system_user
        )
    return "Update completed"

