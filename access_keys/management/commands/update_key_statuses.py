from django.core.management.base import BaseCommand
from django.utils import timezone
from access_keys.models import AccessKey, KeyLog

class Command(BaseCommand):
    help = 'Update access key statuses based on expiry dates'
    
    def handle(self, *args, **kwargs):
        try:
            now = timezone.now().date()
            expired_keys = AccessKey.objects.filter(expiry_date__lt=now, status='active')
            
            for key in expired_keys:
                key.status = 'expired'
                key.save()
                
                # Log the expiration
                KeyLog.objects.create(
                    access_key=key,
                    action=f'Access key {key.key} expired.',
                    user=None  # Adjust this if you need to log a specific user
                )
                
            self.stdout.write(self.style.SUCCESS(f'Successfully marked {expired_keys.count()} keys as expired.'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
