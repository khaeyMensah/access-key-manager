from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import schedule
from datetime import timedelta
# from celery.schedules import crontab



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_key_manager.settings')

app = Celery('access_key_manager')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'

app.conf.beat_schedule = {
    'update_key_statuses': {
        'task': 'access_keys.tasks.update_key_statuses',
        'schedule': schedule(run_every=timedelta(hours=1)),
        'options': {'expires': 3600}
    },
    'monitor_memory': {
        'task': 'access_keys.tasks.monitor_memory',
        'schedule': schedule(run_every=timedelta(hours=1)),
        'options': {'expires': 3600}
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    
