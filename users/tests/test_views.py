from django.utils import timezone
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.tokens import account_activation_token
from access_keys.models import School
from users.models import BillingInformation, User
from unittest.mock import patch

User = get_user_model()

class UserViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.school = School.objects.create(name='Test School')
        
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='password123',
            is_admin=True,
            first_name='Admin',
            last_name='User',
            staff_id='A001'
        )
        
        self.school_personnel_user = User.objects.create_user(
            username='schooluser',
            email='school@example.com',
            password='password123',
            is_school_personnel=True,
            first_name='School',
            last_name='User',
            school=self.school
        )
        
        self.inactive_user = User.objects.create_user(
            username='inactiveuser',
            email='inactive@example.com',
            password='password123',
            is_active=False
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/home.html')

    def test_school_dashboard_view(self):
        self.client.login(username='schooluser', password='password123')
        response = self.client.get(reverse('school_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/school_dashboard.html')

    def test_admin_dashboard_view(self):
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/admin_dashboard.html')


    def test_registration_options_view(self):
        response = self.client.get(reverse('register_options'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register_options.html')

    def test_register_school_personnel_view(self):
        response = self.client.get(reverse('register_school_personnel'))
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'accounts/register.html')

        initial_user_count = User.objects.count()
        
        response = self.client.post(reverse('register_school_personnel'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'A_strong_password123!',
            'password2': 'A_strong_password123!'
        })
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('registration_pending'))
        
        user_count = User.objects.count()
        
        self.assertEqual(user_count, initial_user_count + 1)
        # self.assertEqual(User.objects.count(), 4) 
        self.assertFalse(User.objects.get(username='newuser').is_active)
        self.assertEqual(len(mail.outbox), 1)


    def test_register_admin_view(self):
        response = self.client.get(reverse('register_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

        initial_user_count = User.objects.count()

        response = self.client.post(reverse('register_admin'), {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password1': 'A_strong_password123!',
            'password2': 'A_strong_password123!'
        })
        self.assertEqual(response.status_code, 302)

        user_count = User.objects.count()

        self.assertEqual(user_count, initial_user_count + 1)
        self.assertTrue(User.objects.filter(username='newadmin').exists())
        self.assertRedirects(response, reverse('registration_pending'))
        self.assertFalse(User.objects.get(username='newadmin').is_active)
        self.assertEqual(len(mail.outbox), 1)

    def tearDown(self):
        User.objects.all().delete()

    def test_activate_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.inactive_user.pk))
        token = account_activation_token.make_token(self.inactive_user)
        activation_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        
        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('activation_success'))
        self.inactive_user.refresh_from_db()
        self.assertTrue(self.inactive_user.is_active)

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        response = self.client.post(reverse('login'), {
            'username': 'adminuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_logout_view(self):
        self.client.login(username='adminuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_profile_view(self):
        self.client.login(username='schooluser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_billing_information_view(self):
        billing_info = BillingInformation.objects.create(
            user=self.school_personnel_user, 
            payment_method='card', 
            card_number='1234567890123456', 
            card_expiry=timezone.now().date(), 
            card_cvv='123'
        )
        self.client.login(username='schooluser', password='password123')
        response = self.client.get(reverse('billing_information'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/billing_information.html')
        self.assertContains(response, '**** **** **** 3456')

    @patch('users.models.User.is_profile_complete', return_value=False)
    def test_complete_profile_view_admin(self, mock_is_profile_complete):
        self.client.login(username='adminuser', password='password123')
        
        # GET request to the complete profile view
        response = self.client.get(reverse('complete_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/complete_profile.html')

        # POST request to update profile
        response = self.client.post(reverse('complete_profile'), {
            'first_name': 'UpdatedAdmin',
            'last_name': 'User',
            'email': 'updatedadmin@example.com',
            'staff_id': 'A002',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Refresh the user instance from the database
        self.admin_user.refresh_from_db()
        self.assertEqual(self.admin_user.first_name, 'UpdatedAdmin')
        self.assertEqual(self.admin_user.email, 'updatedadmin@example.com')
        self.assertEqual(self.admin_user.staff_id, 'A002')

    @patch('users.models.User.is_profile_complete', return_value=False)
    def test_complete_profile_view_school_personnel(self, mock_is_profile_complete):
        self.client.login(username='schooluser', password='password123')
        
        # GET request to the complete profile view
        response = self.client.get(reverse('complete_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/complete_profile.html')

        # POST request to update profile
        response = self.client.post(reverse('complete_profile'), {
            'first_name': 'UpdatedSchool',
            'last_name': 'User',
            'email': 'updatedschool@example.com',
            'school': self.school.id,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        
        # Refresh the user instance from the database
        self.school_personnel_user.refresh_from_db()
        self.assertEqual(self.school_personnel_user.first_name, 'UpdatedSchool')
        self.assertEqual(self.school_personnel_user.email, 'updatedschool@example.com')
        self.assertEqual(self.school_personnel_user.school.id, self.school.id)
        
    def test_update_billing_information_view(self):
        billing_info = BillingInformation.objects.create(
            user=self.school_personnel_user, 
            payment_method='mtn_momo', 
            mobile_money_number='1234567890'
        )
        self.client.login(username='schooluser', password='password123')
        response = self.client.post(reverse('update_billing_info'), {
            'payment_method': 'card',
            'card_number': '1234567890123456',
            'card_expiry': '12/25',
            'card_cvv': '123',
        })
        self.assertEqual(response.status_code, 302)
        billing_info.refresh_from_db()
        self.assertEqual(billing_info.payment_method, 'card')
        self.assertEqual(billing_info.card_number, '1234567890123456')
        self.assertEqual(billing_info.card_expiry, '12/25')
        self.assertEqual(billing_info.card_cvv, '123')

            
    def test_update_profile_view(self):
        self.client.login(username='schooluser', password='password123')
        
        response = self.client.get(reverse('update_profile'))
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, 'users/update_profile.html')

        response = self.client.post(reverse('update_profile'), {
            'username': 'schooluser', 
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'newname@example.com'
        })
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('profile'))
        self.school_personnel_user.refresh_from_db()
        self.assertEqual(self.school_personnel_user.first_name, 'New')
        self.assertEqual(self.school_personnel_user.email, 'newname@example.com')