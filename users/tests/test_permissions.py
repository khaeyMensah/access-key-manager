from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

class UserPermissionTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.school_personnel = self.User.objects.create_user(
            username='school_personnel', 
            password='password', 
            is_school_personnel=True,
            email='school_personnel@example.com'  # Add a valid email
        )
        self.admin = self.User.objects.create_user(
            username='admin', 
            password='password', 
            is_admin=True,
            email='admin@example.com'  # Add a valid email
        )

    def test_school_personnel_permission(self):
        permission = Permission.objects.get(codename='can_purchase_access_key')
        self.assertTrue(self.school_personnel.has_perm('users.can_purchase_access_key'))

    def test_admin_permission(self):
        permission = Permission.objects.get(codename='can_revoke_access_key')
        self.assertTrue(self.admin.has_perm('users.can_revoke_access_key'))
