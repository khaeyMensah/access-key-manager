from celery import shared_task
from django.utils import timezone
from access_keys.models import AccessKey, KeyLog
from users.models import User 
from celery.utils.log import get_task_logger


"""
Celery tasks for managing access keys and monitoring worker resources.
"""

logger = get_task_logger(__name__)

@shared_task
def update_key_statuses():
    """
    Update the status of expired access keys and schedule the next run.

    This task checks for expired access keys and updates their status to 'expired'. It also logs the expiration event and schedules the next run based on upcoming expiries.

    Returns:
        str: A message indicating the completion of the task, including the number of expired keys.
    """
    now = timezone.now()
    logger.info(f"Running update_key_statuses at {now}")

    expired_keys = AccessKey.objects.filter(expiry_date__lte=now, status='active')
    expired_count = expired_keys.count()
    logger.info(f"Found {expired_count} expired keys")

    system_user = User.objects.filter(is_superuser=True).first()

    if not system_user:
        logger.error('No admin user found. Please create an admin user.')
        return

    for key in expired_keys:
        key.status = 'expired'
        key.save()
        logger.info(f"Expired key: {key.key}")
        KeyLog.objects.create(
            access_key=key,
            action=f'Access key {key.key} expired for school {key.school.name}',
            user=system_user
        )
        logger.info(f"Updated key {key.key} to expired.")
    logger.info(f'Checked at {timezone.now()}: Updated {expired_keys.count()} keys.')
    