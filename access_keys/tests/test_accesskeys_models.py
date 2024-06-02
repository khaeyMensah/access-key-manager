from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..models import School, AccessKey, KeyLog

User = get_user_model()

class AccessKeyModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_school_personnel=True,
            school=self.school
        )

    def test_access_key_creation(self):
        access_key = AccessKey.objects.create(
            key='ABCD1234',
            school=self.school,
            status='active',
            expiry_date='2024-12-31'
        )
        self.assertEqual(str(access_key), 'ABCD1234 - Test School - active')

    def test_active_key_validation(self):
        AccessKey.objects.create(
            key='ABCD1234',
            school=self.school,
            status='active',
            expiry_date='2024-12-31'
        )
        with self.assertRaises(ValidationError):
            AccessKey.objects.create(
                key='EFGH5678',
                school=self.school,
                status='active',
                expiry_date='2025-06-30'
            )

class KeyLogModelTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            is_school_personnel=True,
            school=self.school
        )
        self.access_key = AccessKey.objects.create(
            key='ABCD1234',
            school=self.school,
            status='active',
            expiry_date='2024-12-31'
        )

    def test_key_log_creation(self):
        key_log = KeyLog.objects.create(
            action='Key generated',
            user=self.user,
            access_key=self.access_key
        )
        self.assertEqual(key_log.action, 'Key generated')
        self.assertEqual(key_log.user, self.user)
        self.assertEqual(key_log.access_key, self.access_key)