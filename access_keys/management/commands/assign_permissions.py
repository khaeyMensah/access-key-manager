from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from users.models import User

class Command(BaseCommand):
    help = 'Assign permissions to users'

    def handle(self, *args, **kwargs):
        try:
            # Assign permissions to school personnel
            school_personnel_permission = Permission.objects.get(codename='can_purchase_access_key')
            school_personnel_users = User.objects.filter(is_school_personnel=True)
            for user in school_personnel_users:
                user.user_permissions.add(school_personnel_permission)

            # Assign permissions to admins
            admin_permission = Permission.objects.get(codename='can_revoke_access_key')
            admin_users = User.objects.filter(is_admin=True)
            for user in admin_users:
                user.user_permissions.add(admin_permission)

            self.stdout.write(self.style.SUCCESS('Successfully assigned permissions to users'))
        except Permission.DoesNotExist:
            self.stdout.write(self.style.ERROR('Permission does not exist'))
