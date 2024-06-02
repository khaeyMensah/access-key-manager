from django.test import TestCase
from django.urls import reverse
from access_keys.models import AccessKey, KeyLog, School
from users.models import User

class AccessKeyTests(TestCase):

    def setUp(self):
        self.school = School.objects.create(name="Test School")
        self.school_user = User.objects.create_user(username='school_user', email='school_user@example.com', password='password123', is_school_personnel=True, school=self.school)
        self.admin_user = User.objects.create_user(username='admin_user', email='admin_user@example.com', password='password123', is_admin=True)
        self.client.login(username='school_user', password='password123')

    def test_create_access_key(self):
        response = self.client.post(reverse('access_keys:purchase_access_key'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AccessKey.objects.filter(assigned_to=self.school_user).exists())

    def test_create_access_key_existing_active(self):
        AccessKey.objects.create(key='123456', assigned_to=self.school_user, school=self.school, status='active', date_of_procurement='2023-01-01', expiry_date='2024-01-01')
        response = self.client.post(reverse('access_keys:purchase_access_key'), follow=True)
        self.assertContains(response, 'You already have an active access key.')
        self.assertEqual(AccessKey.objects.filter(assigned_to=self.school_user).count(), 1)

    def test_view_access_keys(self):
        AccessKey.objects.create(key='123456', assigned_to=self.school_user, school=self.school, status='active', date_of_procurement='2023-01-01', expiry_date='2024-01-01')
        response = self.client.get(reverse('access_keys:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '123456')

    def test_revoke_access_key(self):
        access_key = AccessKey.objects.create(key='123456', assigned_to=self.school_user, school=self.school, status='active', date_of_procurement='2023-01-01', expiry_date='2024-01-01')
        self.client.login(username='admin_user', password='password123')
        response = self.client.post(reverse('access_keys:revoke_access_key', args=[access_key.id]))
        self.assertEqual(response.status_code, 302)
        # self.assertTrue(RevokedAccessKey.objects.filter(access_key=access_key).exists())
        access_key.refresh_from_db()
        self.assertEqual(access_key.status, 'revoked')

    def test_key_log_entry_on_access_key_purchase(self):
        self.client.post(reverse('access_keys:purchase_access_key'))
        self.assertTrue(KeyLog.objects.filter(action__contains='purchased').exists())

    def test_key_log_entry_on_access_key_revoke(self):
        access_key = AccessKey.objects.create(key='123456', assigned_to=self.school_user, school=self.school, status='active', date_of_procurement='2023-01-01', expiry_date='2024-01-01')
        self.client.login(username='admin_user', password='password123')
        self.client.post(reverse('access_keys:revoke_access_key', args=[access_key.id]))
        self.assertTrue(KeyLog.objects.filter(action__contains='revoked').exists())
