from django.test import TestCase
from ..forms import RegistrationForm

class SignUpFormTest(TestCase):
    def setUp(self):
        self.form = RegistrationForm()

    def test_form_has_fields(self):
        expected_fields = ['username', 'email', 'password1', 'password2']
        actual_fields = list(self.form.fields)
        self.assertListEqual(expected_fields, actual_fields, "Form fields do not match expected fields")
