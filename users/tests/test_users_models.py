from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import School, BillingInformation

User = get_user_model()

class UserModelTests(TestCase):
    def test_create_user(self):
        """Test that a new user can be created successfully."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_school_personnel=True
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.is_school_personnel)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test that a new superuser can be created successfully."""
        user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword'
        )
        self.assertEqual(user.username, 'adminuser')
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertFalse(user.is_school_personnel)

    def test_create_duplicate_user(self):
        """Test that creating a duplicate user raises an exception."""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpassword'
            )

class SchoolModelTests(TestCase):
    def test_school_creation(self):
        """Test that a new school can be created successfully."""
        school = School.objects.create(name='Test School')
        self.assertEqual(str(school), 'Test School')

    def test_school_users_relationship(self):
        """Test the relationship between a school and its associated users."""
        school = School.objects.create(name='Test School')
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password',
            school=school
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password',
            school=school
        )
        self.assertEqual(school.users.count(), 2)
        self.assertIn(user1, school.users.all())
        self.assertIn(user2, school.users.all())

class BillingInformationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_create_billing_information_card(self):
        billing_info = BillingInformation.objects.create(
            user=self.user,
            payment_method='Card',
            card_number='1234567890123456',
            card_expiry='2024-12-31',
            card_cvv='123'
        )
        self.assertEqual(billing_info.user, self.user)
        self.assertEqual(billing_info.payment_method, 'Card')
        self.assertEqual(billing_info.card_number, '1234567890123456')

    def test_create_billing_information_momo(self):
        billing_info = BillingInformation.objects.create(
            user=self.user,
            payment_method='MTN',
            mobile_money_number='0241234567'
        )
        self.assertEqual(billing_info.user, self.user)
        self.assertEqual(billing_info.payment_method, 'MTN')
        self.assertEqual(billing_info.mobile_money_number, '0241234567')
