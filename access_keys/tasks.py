from celery import shared_task
from django.utils import timezone
from datetime import datetime, time, timedelta
from access_keys.models import AccessKey, KeyLog
from users.models import User 
from celery.utils.log import get_task_logger
import psutil

logger = get_task_logger(__name__)

@shared_task
def update_key_statuses():
    now = timezone.now()
    logger.info(f"Running update_key_statuses at {now}")

    # Check and update expired keys
    expired_keys = AccessKey.objects.filter(expiry_date__lte=now.date(), status='active')
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

    # Schedule next run based on upcoming expiries
    next_expiry = AccessKey.objects.filter(expiry_date__gt=now.date(), status='active').order_by('expiry_date').first()

    if next_expiry:
        time_until_next_expiry = next_expiry.expiry_date - now.date()
        if time_until_next_expiry.days == 0:
            # If next expiry is today, check again in an hour
            next_run = now + timedelta(hours=1)
        else:
            # Schedule for the start of the next expiry day
            next_run = datetime.combine(next_expiry.expiry_date, time.min)
            next_run = timezone.make_aware(next_run)
        
        logger.info(f"Scheduling next run at {next_run}")
        update_key_statuses.apply_async(eta=next_run)
    else:
        logger.info("No upcoming expiries. Next check will be in 1 hour.")

    return f"Update completed. Expired {expired_count} keys."

@shared_task
def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    cpu_usage = process.cpu_percent(interval=1)
    logger.info(f"Celery worker memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
    logger.info(f"Celery worker CPU usage: {cpu_usage:.2f}%")