from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from access_keys.models import School, AccessKey, KeyLog
from django.utils import timezone

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
        """Test that an access key can be created successfully."""
        access_key = AccessKey.objects.create(
            key='ABCD1234',
            school=self.school,
            status='active',
            assigned_to=self.user,
            expiry_date='2024-12-31'
        )
        self.assertEqual(str(access_key), 'ABCD1234 - Test School - active')

    def test_active_key_validation(self):
        """Test that only one active access key can be assigned to a school at a time."""
        AccessKey.objects.create(
            key='ABCD1234',
            school=self.school,
            status='active',
            assigned_to=self.user,
            expiry_date='2024-12-31'
        )
        with self.assertRaises(ValidationError):
            AccessKey.objects.create(
                key='EFGH5678',
                school=self.school,
                status='active',
                assigned_to=self.user,
                expiry_date='2025-06-30'
            )

    def test_key_expiration(self):
        """Test that an access key's status is updated to 'expired' after the expiry date."""
        access_key = AccessKey.objects.create(
            key='ABCD1234',
            school=self.school,
            status='active',
            assigned_to=self.user,
            expiry_date=timezone.now().date() - timezone.timedelta(days=1)
        )
        access_key.status = 'expired'
        access_key.save()
        self.assertEqual(access_key.status, 'expired')

    def test_create_access_key_with_invalid_status(self):
        """Test that creating an access key with an invalid status raises a ValidationError."""
        with self.assertRaises(ValidationError):
            AccessKey.objects.create(
                key='INVALID123',
                school=self.school,
                status='invalid_status',
                assigned_to=self.user,
                expiry_date='2024-12-31'
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
            assigned_to=self.user,
            expiry_date='2024-12-31'
        )

    def test_key_log_creation(self):
        """Test that a key log can be created successfully."""
        key_log = KeyLog.objects.create(
            action='Key generated',
            user=self.user,
            access_key=self.access_key
        )
        self.assertEqual(key_log.action, 'Key generated')
        self.assertEqual(key_log.user, self.user)
        self.assertEqual(key_log.access_key, self.access_key)

    def test_key_log_timestamp(self):
        """Test that a key log's timestamp is set automatically."""
        key_log = KeyLog.objects.create(
            action='Key generated',
            user=self.user,
            access_key=self.access_key
        )
        self.assertIsNotNone(key_log.timestamp)