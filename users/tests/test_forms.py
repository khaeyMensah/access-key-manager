from django.test import TestCase
from django.contrib.auth import get_user_model
from users.forms import RegistrationForm, ProfileForm, ProfileUpdateForm, BillingInformationForm
from users.models import School

User = get_user_model()

class RegistrationFormTest(TestCase):

    def test_registration_form_valid(self):
        form_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
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
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword123')

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
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpassword123')

    def test_billing_information_form_valid_mtn_momo(self):
        form_data = {
            'email': self.user.email,
            'payment_method': 'mtn_momo',
            'mobile_money_number': '1234567890',
            'confirm_purchase': True
        }
        form = BillingInformationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_billing_information_form_invalid_mtn_momo(self):
        form_data = {
            'email': self.user.email,
            'payment_method': 'mtn_momo',
            'confirm_purchase': True
        }
        form = BillingInformationForm(data=form_data)
        form.instance.user = self.user
        self.assertFalse(form.is_valid())
        self.assertIn('mobile_money_number', form.errors)

    def test_billing_information_form_valid_card(self):
        form_data = {
            'email': self.user.email,
            'payment_method': 'card',
            'card_number': '1234567890123456',
            'card_expiry': '12/25',
            'card_cvv': '123',
            'confirm_purchase': True
        }
        form = BillingInformationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_billing_information_form_invalid_card(self):
        form_data = {
            'email': self.user.email,
            'payment_method': 'card',
            'confirm_purchase': True
        }
        form = BillingInformationForm(data=form_data)
        form.instance.user = self.user
        self.assertFalse(form.is_valid())
        self.assertIn('card_number', form.errors)
        self.assertIn('card_expiry', form.errors)
        self.assertIn('card_cvv', form.errors)

    def test_billing_information_form_invalid_mixed(self):
        form_data = {
            'email': self.user.email,
            'payment_method': 'mtn_momo',
            'mobile_money_number': '1234567890',
            'card_number': '1234567890123456',
            'card_expiry': '12/25',
            'card_cvv': '123',
            'confirm_purchase': True
        }
        form = BillingInformationForm(data=form_data)
        form.instance.user = self.user
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Check if non-field error is raised
