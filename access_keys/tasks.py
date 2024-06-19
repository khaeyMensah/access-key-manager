# access_keys/tasks.py
from celery import shared_task
from django.utils import timezone
from access_keys.models import AccessKey, KeyLog
from django.contrib.auth.models import User, Permission

@shared_task
def update_key_statuses():
    now = timezone.now().date()
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

@shared_task
def assign_permissions():
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
