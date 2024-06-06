from celery import shared_task
from django.utils import timezone
from .models import AccessKey

@shared_task
def update_key_statuses():
    now = timezone.now()
    expired_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')
    expired_keys.update(status='expired')
