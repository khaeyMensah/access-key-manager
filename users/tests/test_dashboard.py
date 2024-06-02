from django.test import TestCase
from django.urls import reverse
from access_keys.models import School
from users.models import User

class DashboardTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.school_user = User.objects.create_user(username='school_user', password='password123', is_school_personnel=True, school=self.school)
        self.admin_user = User.objects.create_user(username='admin_user', password='password123', is_admin=True)

    def test_school_personnel_access(self):
        self.client.login(username='school_user', password='password123')
        response = self.client.get(reverse('school_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_admin_access(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_school_personnel_access_denied_to_admin_dashboard(self):
        self.client.login(username='school_user', password='password123')
        response = self.client.get(reverse('admin_dashboard'), follow=True)
        self.assertRedirects(response, expected_url='/login/?next=/admin_dashboard/')
        # If there's a specific error message on the redirected page, assert that
        self.assertContains(response, 'You do not have permission to view this page.')

    def test_admin_access_denied_to_school_dashboard(self):
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('school_dashboard'), follow=True)
        self.assertRedirects(response, expected_url='/login/?next=/school_dashboard/')
        # If there's a specific error message on the redirected page, assert that
        self.assertContains(response, 'You do not have permission to view this page.')
