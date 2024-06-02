from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from access_keys.models import AccessKey, School

User = get_user_model()

class APITests(TestCase):

    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.user = User.objects.create_user(username='user', email='user@example.com', password='password123', is_school_personnel=True, school=self.school)
        self.access_key = AccessKey.objects.create(key='123456', assigned_to=self.user, school=self.school, status='active', date_of_procurement='2023-01-01', expiry_date='2024-01-01')

    def test_key_status_api(self):
        response = self.client.get(reverse('api:key_status', kwargs={'key': self.access_key.key}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'active'})

    def test_key_status_api_invalid_key(self):
        response = self.client.get(reverse('api:key_status', kwargs={'key': 'invalid'}))
        self.assertEqual(response.status_code, 404)
