import unittest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from users.models import User
from access_keys.tasks import update_key_statuses, monitor_memory 


class TestCeleryTasks(unittest.TestCase):

    @patch('access_keys.models.AccessKey.objects')
    @patch('users.models.User.objects')
    @patch('access_keys.models.KeyLog.objects.create')
    @patch('access_keys.tasks.update_key_statuses.apply_async')
    def test_update_key_statuses(self, mock_apply_async, mock_keylog_create, mock_user_objects, mock_accesskey_objects):
        # Setup
        now = timezone.now()
        mock_expired_key = MagicMock(key='expired_key', school=MagicMock(name='Test School'))
        mock_active_key = MagicMock(expiry_date=now + timedelta(days=1))
        mock_accesskey_objects.filter.side_effect = [
            MagicMock(count=lambda: 1, __iter__=lambda self: iter([mock_expired_key])),  # expired keys
            MagicMock(__iter__=lambda self: iter([mock_active_key]))  # active keys
        ]
        mock_user_objects.filter.return_value.first.return_value = MagicMock(spec=User)

        # Execute
        result = update_key_statuses()

        # Assert
        self.assertEqual(result, "Update completed. Expired 1 keys.")
        mock_expired_key.save.assert_called_once()
        mock_keylog_create.assert_called_once()
        mock_apply_async.assert_called_once()

    @patch('psutil.Process')
    def test_monitor_memory(self, mock_process):
        # Setup
        mock_process.return_value.memory_info.return_value = MagicMock(rss=104857600)  # 100 MB
        mock_process.return_value.cpu_percent.return_value = 5.0

        # Execute
        with self.assertLogs(level='INFO') as log:
            monitor_memory()

        # Assert
        self.assertIn("Celery worker memory usage: 100.00 MB", log.output[0])
        self.assertIn("Celery worker CPU usage: 5.00%", log.output[1])

if __name__ == '__main__':
    unittest.main()