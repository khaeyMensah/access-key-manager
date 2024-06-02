from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from access_keys.models import School

User = get_user_model()

class UserTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.school_user = User.objects.create_user(username='school_user', email='school_user@example.com', password='password123', is_school_personnel=True, school=self.school)
        self.admin_user = User.objects.create_user(username='admin_user', email='admin_user@example.com', password='password123', is_admin=True)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_registration_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword124'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'password2', "The two password fields didn’t match.")

    def test_admin_registration(self):
        response = self.client.post(reverse('admin_register'), {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newadmin').exists())

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'school_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_admin_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_user',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_user_logout(self):
        self.client.login(username='school_user', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_password_reset(self):
        response = self.client.post(reverse('password_reset'), {'email': 'school_user@example.com'})
        self.assertEqual(response.status_code, 302)

    def test_password_change(self):
        self.client.login(username='school_user', password='password123')
        response = self.client.post(reverse('password_change'), {
            'old_password': 'password123',
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302)
        self.school_user.refresh_from_db()
        self.assertTrue(self.school_user.check_password('newpassword123'))

    def test_complete_profile(self):
        self.client.login(username='school_user', password='password123')
        response = self.client.post(reverse('complete_profile'), {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'new_email@example.com',
            'school': self.school.id
        })
        self.assertEqual(response.status_code, 302)
        self.school_user.refresh_from_db()
        self.assertEqual(self.school_user.first_name, 'New')
        self.assertEqual(self.school_user.last_name, 'Name')
        self.assertEqual(self.school_user.email, 'new_email@example.com')
