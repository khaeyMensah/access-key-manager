# users/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from access_keys.models import AccessKey
from users.models import User, School

class CheckAccessKeyStatusViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='school@example.com', password='password123')
        self.school = School.objects.create(user=self.user)
        self.access_key = AccessKey.objects.create(
            school=self.school,
            key='some-key-value',
            status='active',
            procurement_date='2024-05-30T12:34:56Z',
            expiry_date='2025-05-30T12:34:56Z'
        )

    def test_check_access_key_status(self):
        response = self.client.get(reverse('key_status'), {'school_email': 'school@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'some-key-value')

    def test_no_active_key(self):
        self.access_key.status = 'expired'
        self.access_key.save()
        response = self.client.get(reverse('key_status'), {'school_email': 'school@example.com'})
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'No active access key found.')

    def test_school_not_found(self):
        response = self.client.get(reverse('key_status'), {'school_email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, 'School not found.')

    def test_invalid_request_method(self):
        response = self.client.post(reverse('key_status'), {'school_email': 'school@example.com'})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Invalid request method.')
