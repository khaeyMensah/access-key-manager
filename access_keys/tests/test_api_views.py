from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User, School
from access_keys.models import AccessKey
from django.utils import timezone

class AccessKeyAPITests(TestCase):
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
        self.access_key = AccessKey.objects.create(
            school=self.school,
            key='TESTKEY123',
            status='active',
            assigned_to=self.user,
            procurement_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timezone.timedelta(days=30),
            price=100
        )

    def test_check_access_key_valid(self):
        """Test that the API returns the correct access key details for a valid school email."""
        url = reverse('access_keys:key_status', kwargs={'email': 'school@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['key'], self.access_key.key)
        self.assertEqual(response.data['status'], 'active')

    def test_check_access_key_invalid_email(self):
        """Test that the API returns a 404 error for an invalid school email."""
        url = reverse('access_keys:key_status', kwargs={'email': 'invalid@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found.')

    def test_check_access_key_no_active_key(self):
        """Test that the API returns a 404 error if there is no active access key for the school."""
        self.access_key.status = 'expired'
        self.access_key.save()
        url = reverse('access_keys:key_status', kwargs={'email': 'school@example.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'No active access key found.')

    def test_check_access_key_missing_email(self):
        """Test that the API returns a 400 error if the email parameter is missing."""
        url = reverse('access_keys:key_status')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'email parameter is required.')