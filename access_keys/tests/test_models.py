import datetime
from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from access_keys.models import School, AccessKey, KeyLog
from django.utils import timezone

User = get_user_model()

class AccessKeyModelTest(TestCase):

    def setUp(self):
        self.school = School.objects.create(name='Test School')
        self.user = User.objects.create(username='test_user', email='test_user@example.com')
        self.access_key = AccessKey.objects.create(
            key='test_key',
            school=self.school,
            assigned_to=self.user,
            expiry_date=timezone.now() - timezone.timedelta(days=1),
            price=settings.ACCESS_KEY_PRICE
        )

class KeyLogModelTest(TestCase):

    def test_key_log_creation(self):
        access_key = AccessKey.objects.create(
            key='test_key',
            school=School.objects.create(name='Test School'),
            assigned_to=User.objects.create(username='test_user', email='test_user1@example.com'),
            expiry_date=timezone.now() + datetime.timedelta(days=30),
            price=settings.ACCESS_KEY_PRICE
        )

        key_log = KeyLog.objects.create(
            action='test_action',
            user=User.objects.create(username='test_user2', email='test_user2@example.com'),
            access_key=access_key
        )

        self.assertEqual(KeyLog.objects.count(), 1)
        self.assertEqual(key_log.action, 'test_action')
        self.assertEqual(key_log.user.username, 'test_user2')
        self.assertEqual(key_log.access_key.key, 'test_key')
        self.assertEqual(key_log.access_key.school.name, 'Test School')

    def test_key_log_timestamp(self):
        access_key = AccessKey.objects.create(
            key='test_key2',
            school=School.objects.create(name='Test School2'),
            assigned_to=User.objects.create(username='test_user3', email='test_user3@example.com'),
            expiry_date=timezone.now() + datetime.timedelta(days=30),
            price=settings.ACCESS_KEY_PRICE
        )

        key_log = KeyLog.objects.create(
            action='test_action2',
            user=User.objects.create(username='test_user4', email='test_user4@example.com'),
            access_key=access_key
        )
        self.assertTrue(timezone.now() - key_log.timestamp < datetime.timedelta(seconds=5))

    def test_key_log_related_name(self):
        access_key = AccessKey.objects.create(
            key='test_key3',
            school=School.objects.create(name='Test School3'),
            assigned_to=User.objects.create(username='test_user5', email='test_user5@example.com'),
            expiry_date=timezone.now() + datetime.timedelta(days=30),
            price=settings.ACCESS_KEY_PRICE
        )

        key_log = KeyLog.objects.create(
            action='test_action3',
            user=User.objects.create(username='test_user6', email='test_user6@example.com'),
            access_key=access_key
        )

        self.assertEqual(AccessKey.objects.get(pk=access_key.pk).key_logs.count(), 1)

    def test_key_log_unique_action(self):
        access_key = AccessKey.objects.create(
            key='test_key4',
            school=School.objects.create(name='Test School4'),
            assigned_to=User.objects.create(username='test_user7', email='test_user7@example.com'),
            expiry_date=timezone.now() + datetime.timedelta(days=30),
            price=settings.ACCESS_KEY_PRICE
        )

        KeyLog.objects.create(
            action='test_action4',
            user=User.objects.create(username='test_user8', email='test_user8@example.com'),
            access_key=access_key
        )

    def test_key_log_user_assignment(self):
        access_key = AccessKey.objects.create(
            key='test_key5',
            school=School.objects.create(name='Test School5'),
            assigned_to=User.objects.create(username='test_user10', email='test_user10@example.com'),
            expiry_date=timezone.now() + datetime.timedelta(days=30),
            price=settings.ACCESS_KEY_PRICE
        )

        key_log = KeyLog.objects.create(
            action='test_action5',
            user=User.objects.create(username='test_user11', email='test_user11@example.com'),
            access_key=access_key
        )

        self.assertIsNotNone(key_log.user)
