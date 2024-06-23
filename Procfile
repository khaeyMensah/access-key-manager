web: gunicorn access_key_manager.wsgi:application --log-file -
worker: celery -A access_key_manager worker --loglevel=info
beat: celery -A access_key_manager beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
