from django.test import TestCase
from django.urls import reverse
from access_keys.models import School
from users.models import User

class EdgeCaseTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.school_user = User.objects.create_user(username='school_user', password='password123', is_school_personnel=True, school=self.school)
        self.admin_user = User.objects.create_user(username='admin_user', password='password123', is_admin=True)

    def test_duplicate_email_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'school_user@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', "User with this Email already exists.")

    def test_inactive_account_login(self):
        self.school_user.is_active = False
        self.school_user.save()
        response = self.client.post(reverse('login'), {
            'username': 'school_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_login_with_wrong_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'school_user',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')
