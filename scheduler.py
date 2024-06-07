import time
from datetime import datetime
import django
import os
from django.utils import timezone

# Initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_key_manager.settings')
django.setup()

from access_keys.models import AccessKey, KeyLog
from users.models import User

def update_key_statuses():
    now = timezone.now()
    print(f"Checking for expired keys at {now}")
    expired_keys = AccessKey.objects.filter(status='active', expiry_date__lt=now)
    print(f"Found {expired_keys.count()} expired keys.")
    
    # Retrieve the system user to associate with the log
    system_user = User.objects.filter(is_admin=True).first()  # Ensure this user exists
    
    if not system_user:
        print("No admin user found. Please create an admin user.")
        return

    for key in expired_keys:
        key.status = 'expired'
        key.save()
        # Log the expiration event
        KeyLog.objects.create(
            access_key=key,
            action=f'Access key {key.key} expired for school {key.school.name}',
            user=system_user  # Set the user field to system_user
        )
        print(f"Updated key {key.key} to expired.")
    print(f'Checked at {datetime.now()}: Updated {expired_keys.count()} keys.')

while True:
    update_key_statuses()
    time.sleep(60)  # Wait one minute before checking again
