from django.core.management.base import BaseCommand
from django.utils import timezone
from access_keys.models import AccessKey

class Command(BaseCommand):
    help = 'update access key statuses bases on expiry dates'
    
    def handle(self, *args, **kwargs):
        now = timezone.now()
        expiry_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')
        expiry_keys.update(status='expired')
        self.stdout.write(self.style.SUCCESS('Successfully updated key statuses'))