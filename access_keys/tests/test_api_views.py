from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, School
from access_keys.models import AccessKey
from django.utils import timezone

class CheckAccessKeyStatusViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create_user(
            username='school_user',
            email='school@example.com',
            password='schoolpassword',
            is_school_personnel=True,
            school=self.school
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_admin=True
        )
        self.access_key = AccessKey.objects.create(
            school=self.school,
            key='TESTKEY123',
            status='active',
            assigned_to=self.user,
            procurement_date=timezone.now(),
            expiry_date=timezone.now() + timezone.timedelta(days=30),
            price=100
        )

    def login_admin(self):
        self.client.login(username='admin', password='adminpassword')

    def test_check_access_key_valid(self):
        self.login_admin()
        url = reverse('access_keys:key_status', kwargs={'email': 'school@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['key'], self.access_key.key)
        self.assertEqual(response.data['status'], 'active')

    def test_check_access_key_invalid_email(self):
        self.login_admin()
        url = reverse('access_keys:key_status', kwargs={'email': 'invalid@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found.')

    def test_check_access_key_no_active_key(self):
        self.login_admin()
        self.access_key.status = 'expired'
        self.access_key.save()
        url = reverse('access_keys:key_status', kwargs={'email': 'school@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'No active access key found.')

    def test_check_access_key_missing_email(self):
        self.login_admin()
        url = reverse('access_keys:key_status', kwargs={'email': 'none'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Email parameter is required.')
        
    
    def test_check_access_key_no_email_parameter(self):
        self.login_admin()
        url = reverse('access_keys:key_status', kwargs={'email': 'no_email_param'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found.')
        
        
    def test_check_access_key_user_not_associated_with_school(self):
        self.login_admin()
        user_without_school = User.objects.create_user(
            username='no_school_user',
            email='no_school@example.com',
            password='noschoolpassword'
        )
        url = reverse('access_keys:key_status', kwargs={'email': 'no_school@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User is not associated with any school.')

    def test_check_access_key_unauthorized(self):
        url = reverse('access_keys:key_status', kwargs={'email': 'school@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # Redirect to login page

        self.client.login(username='school_user', password='schoolpassword')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 