# users/tests/test_views.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import School, BillingInformation
from django.contrib.auth import get_user

User = get_user_model()

class UserViewsTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Test School')
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_admin=True
        )
        self.school_user = User.objects.create_user(
            username='school_user',
            email='school@example.com',
            password='schoolpassword',
            is_school_personnel=True,
            school=self.school
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/home.html')

    def test_school_dashboard_view(self):
        self.client.login(email='school@example.com', password='schoolpassword')
        response = self.client.get(reverse('school_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/school_dashboard.html')

    def test_admin_dashboard_view(self):
        self.client.login(email='admin@example.com', password='adminpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/admin_dashboard.html')

    def test_registration_view(self):
        response = self.client.get(reverse('register_options'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_options.html')

    def test_register_school_personnel_view(self):
        response = self.client.post(reverse('register_school_personnel'), {
            'username': 'newschooluser',
            'email': 'newschooluser@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(email='newschooluser@example.com').exists())

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'school_user',
            'password': 'schoolpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)

    def test_logout_view(self):
        self.client.login(email='school@example.com', password='schoolpassword')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)

    def test_profile_view(self):
        self.client.login(email='school@example.com', password='schoolpassword')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

    def test_billing_information_view(self):
        billing_info = BillingInformation.objects.create(
            user=self.school_user,
            payment_method='Card',
            card_number='1234567890123456',
            card_expiry='2024-12-31',
            card_cvv='123'
        )
        self.client.login(email='school@example.com', password='schoolpassword')
        response = self.client.get(reverse('billing_information'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/billing_information.html')

    def test_confirm_billing_information_view(self):
        self.client.login(email='school@example.com', password='schoolpassword')
        response = self.client.post(reverse('confirm_billing_info'), {
            'payment_method': 'Card',
            'card_number': '1234567890123456',
            'card_expiry': '2024-12-31',
            'card_cvv': '123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful billing info update
        billing_info = BillingInformation.objects.get(user=self.school_user)
        self.assertEqual(billing_info.card_number, '1234567890123456')
