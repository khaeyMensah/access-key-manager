from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from access_keys.models import AccessKey
from users.models import School, User

User = get_user_model()


class PurchaseAccessKeyViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.school_user = User.objects.create_user(
            username='schooluser',
            email='school@example.com',
            password='testpassword',
            is_school_personnel=True
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpassword',
            is_admin=True
        )
        self.school = School.objects.create(name='Test School')
        self.school.users.set([self.school_user])
        
    def test_only_school_personnel_can_purchase_access_key(self):
        self.client.force_login(self.school_user)
        response = self.client.get(reverse('access_keys:purchase_access_key'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('school_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_school_cannot_purchase_multiple_active_keys(self):
        self.client.force_login(self.school_user)
        AccessKey.objects.create(
            key='TEST123456789',
            school=self.school,
            status='active',
            assigned_to=self.school_user,
            procurement_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timezone.timedelta(days=30),
            price=100.00
        )
        response = self.client.get(reverse('access_keys:purchase_access_key'))
        self.assertRedirects(response, reverse('school_dashboard'))

        
class RevokeAccessKeyViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpassword',
            is_admin=True
        )
        self.school_user = User.objects.create_user(
            username='schooluser',
            email='school@example.com',
            password='testpassword',
            is_school_personnel=True
        )
        self.school = School.objects.create(name='Test School')
        self.school.users.set([self.school_user])
        self.access_key = AccessKey.objects.create(
            key='TEST123456789',
            school=self.school,
            status='active',
            assigned_to=self.school_user,
            procurement_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timezone.timedelta(days=30),
            price=100.00
        )

    def test_only_admin_can_revoke_access_key(self):
        self.client.force_login(self.school_user)
        response = self.client.get(reverse('access_keys:revoke_access_key', args=[self.access_key.id]))
        # self.assertEqual(response.status_code, 302)  # Redirect expected
        self.assertEqual(response.status_code, 403)  # Forbidden for school user
        
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('access_keys:revoke_access_key', args=[self.access_key.id]))
        self.assertEqual(response.status_code, 200)

    def test_revoke_access_key_success(self):
        self.client.force_login(self.admin_user)

        # Step 1: Get the revoke access key confirmation page
        response = self.client.get(reverse('access_keys:revoke_access_key', args=[self.access_key.id]))
        self.assertEqual(response.status_code, 200)

        # Step 2: Submit the confirmation form to revoke the access key
        response = self.client.post(reverse('access_keys:revoke_access_key', args=[self.access_key.id]), follow=True)
        self.assertRedirects(response, reverse('admin_dashboard'))

        # Step 3: Follow the redirect and ensure the final response is 200
        final_response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(final_response.status_code, 200)

        access_key = AccessKey.objects.get(id=self.access_key.id)
        self.assertEqual(access_key.status, 'revoked')
        self.assertIsNotNone(access_key.revoked_by)
        self.assertIsNotNone(access_key.revoked_on)


class CheckAccessKeyStatusViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='testpassword',
            is_admin=True
        )
        self.school_user = User.objects.create_user(
            username='schooluser',
            email='school@example.com',
            password='testpassword',
            is_school_personnel=True
        )
        self.school = School.objects.create(name='Test School')
        self.school.users.set([self.school_user])
        self.active_key = AccessKey.objects.create(
            key='TEST123456789',
            school=self.school,
            status='active',
            assigned_to=self.school_user,
            procurement_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timezone.timedelta(days=30),
            price=100.00
        )

    def test_only_admin_can_check_access_key_status(self):
        self.client.force_login(self.school_user)
        response = self.client.get(reverse('access_keys:key_status', args=['school@example.com']))
        self.assertEqual(response.status_code, 403)  # Forbidden

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('access_keys:key_status', args=['school@example.com']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['key'], 'TEST123456789')

    def test_active_key_found(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('access_keys:key_status', args=['school@example.com']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['key'], 'TEST123456789')

    def test_no_active_key_found(self):
        self.active_key.delete()
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('access_keys:key_status', args=['school@example.com']))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'No active access key found.'})

    def test_invalid_email(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('access_keys:key_status', args=['invalid@email.com']))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {'error': 'User not found.'})

