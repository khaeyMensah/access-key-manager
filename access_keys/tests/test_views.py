from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from unittest.mock import patch, MagicMock
from decimal import Decimal
from access_keys.models import AccessKey, KeyLog
from users.models import School, BillingInformation

User = get_user_model()

class PurchaseAccessKeyViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.school = School.objects.create(name='Test School')
        self.school.users.add(self.user)
        self.user.is_school_personnel = True
        self.user.save()

        # Assigning permissions
        permission = Permission.objects.get(codename='can_purchase_access_key')
        self.user.user_permissions.add(permission)
            
    @patch.object(User, 'is_profile_complete', return_value=True)
    def test_only_school_personnel_can_purchase_access_key(self,  mock_is_profile_complete):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('access_keys:purchase_access_key'))
        self.assertEqual(response.status_code, 200)


    @patch.object(User, 'is_profile_complete', return_value=True)
    def test_school_cannot_purchase_multiple_active_keys(self, mock_is_profile_complete):
        AccessKey.objects.create(
            school=self.school,
            status='active',
            key='test_key',
            assigned_to=self.user,
            expiry_date=timezone.now().date() + timezone.timedelta(days=365),
            price=100.00
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('access_keys:purchase_access_key'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('school_dashboard'))


class InitializePaymentViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.school = School.objects.create(name='Test School')
        self.school.users.add(self.user)
        self.user.is_school_personnel = True
        self.user.save()
        BillingInformation.objects.create(user=self.user)

        # Assigning permissions
        permission = Permission.objects.get(codename='can_purchase_access_key')
        self.user.user_permissions.add(permission)

    @patch('access_keys.views.requests.post')
    def test_initialize_payment_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': True,
            'data': {'authorization_url': 'https://paystack.com/pay/test'}
        }
        mock_post.return_value = mock_response

        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('access_keys:initialize_payment'))
        self.assertRedirects(response, 'https://paystack.com/pay/test', fetch_redirect_response=False)
        

class PaystackCallbackViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.school = School.objects.create(name='Test School')
        self.school.users.add(self.user)
        self.user.is_school_personnel = True
        self.user.save()

    @patch('access_keys.views.requests.get')
    def test_paystack_callback_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': True,
            'data': {
                'amount': 10000,
                'customer': {'email': 'test@example.com'}
            }
        }
        mock_get.return_value = mock_response

        response = self.client.get(reverse('access_keys:paystack_callback') + '?reference=test_ref')
        self.assertRedirects(response, reverse('school_dashboard'), fetch_redirect_response=False)
        self.assertTrue(AccessKey.objects.filter(school=self.school, status='active').exists())

class RevokeAccessKeyViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='adminpass123')
        self.admin_user.is_admin = True
        self.admin_user.save()

        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.user.save()
        self.school.users.add(self.user)
        
        self.access_key = AccessKey.objects.create(
            key='testkey123',
            school=self.school,
            status='active',
            assigned_to=self.user,
            expiry_date=timezone.now() + timezone.timedelta(days=30),
            price=Decimal('100.00')
        )

        # Assigning permissions
        permission = Permission.objects.get(codename='can_revoke_access_key')
        self.admin_user.user_permissions.add(permission)

    @patch.object(User, 'is_profile_complete', return_value=True)
    def test_revoke_access_key_view(self, mock_is_profile_complete):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('access_keys:revoke_access_key', args=[self.access_key.id]))
        
        # Ensure the redirection is correct
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'), status_code=302)

        self.access_key.refresh_from_db()
        self.assertEqual(self.access_key.status, 'revoked')
        self.assertTrue(KeyLog.objects.filter(access_key=self.access_key, action__contains='revoked').exists())

    @patch.object(User, 'is_profile_complete', return_value=True)
    def test_only_admin_can_revoke_access_key(self, mock_is_profile_complete):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('access_keys:revoke_access_key', args=[self.access_key.id]))
        self.assertEqual(response.status_code, 403)