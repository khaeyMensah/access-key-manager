from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_key_manager.settings')

app = Celery('access_key_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_key_statuses': {
        'task': 'access_keys.tasks.update_key_statuses',
        'schedule': crontab(minute=0, hour=0),  # Run every day at midnight
    },
    'assign_permissions': {
        'task': 'access_keys.tasks.assign_permissions',
        'schedule': crontab(minute=0, hour=8, day_of_week=1),  # Run every Monday at 8 AM
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
