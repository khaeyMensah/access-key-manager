from django.test import TestCase
from django.contrib.auth import get_user_model
from users.forms import RegistrationForm, ProfileForm, ProfileUpdateForm, BillingInformationForm
from users.models import School, BillingInformation

User = get_user_model()

class RegistrationFormTest(TestCase):

    def test_registration_form_valid(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class ProfileFormTest(TestCase):

    def setUp(self):
        self.school = School.objects.create(name='Test School')

    def test_profile_form_valid(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'school': self.school.id,
        }
        form = ProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_form_invalid(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': '',
            'school': self.school.id,
        }
        form = ProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class ProfileUpdateFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def test_profile_update_form_valid(self):
        form_data = {
            'username': 'updateduser',
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_profile_update_form_invalid(self):
        form_data = {
            'username': '',
            'email': 'updateduser@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        form = ProfileUpdateForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class BillingInformationFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword')

    def test_billing_information_form_valid(self):
        form_data = {
            'email': 'testuser@example.com',
            'payment_method': 'MTN',
            'mobile_money_number': '1234567890'
        }
        form = BillingInformationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_billing_information_form_invalid(self):
        form_data = {
            'email': '',
            'payment_method': 'Card',
            'card_number': '1234567890123456',
            'card_expiry': '2025-12-31',
            'card_cvv': '123'
        }
        form = BillingInformationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
