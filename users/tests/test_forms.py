# from django.test import TestCase
# from users.forms import RegistrationForm, LoginForm, UserCompleteForm, BillingInformationForm
# from users.models import User

# class RegistrationFormTests(TestCase):
#     def test_valid_form(self):
#         """Test that the registration form is valid with correct data."""
#         form_data = {
#             'username': 'newuser',
#             'email': 'newuser@example.com',
#             'password1': 'complexpassword123',
#             'password2': 'complexpassword123'
#         }
#         form = RegistrationForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_invalid_form(self):
#         """Test that the registration form is invalid with mismatched passwords."""
#         form_data = {
#             'username': 'newuser',
#             'email': 'newuser@example.com