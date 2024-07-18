from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from access_keys.models import AccessKey, KeyLog
from users.models import User 
from celery.utils.log import get_task_logger
import psutil


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

    next_expiry = AccessKey.objects.filter(expiry_date__gt=now, status='active').order_by('expiry_date').first()

    if next_expiry:
        next_run = next_expiry.expiry_date
        logger.info(f"Scheduling next run at {next_run}")
        update_key_statuses.apply_async(eta=next_run)
    else:
        next_run = now + timedelta(hours=1)
        logger.info("No upcoming expiries. Next check will be in 1 hour.")
        update_key_statuses.apply_async(eta=next_run)

    return f"Update completed. Expired {expired_count} keys."

# @shared_task
# def monitor_memory():
#     """
#     Monitor the memory and CPU usage of the Celery worker.

#     This task uses the psutil library to retrieve the memory and CPU usage of the Celery worker process and logs the information.

#     Returns:
#         None
#     """
#     process = psutil.Process()
#     memory_info = process.memory_info()
#     cpu_usage = process.cpu_percent(interval=1)
#     logger.info(f"Celery worker memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
#     logger.info(f"Celery worker CPU usage: {cpu_usage:.2f}%")
