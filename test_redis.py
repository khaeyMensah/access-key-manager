import redis
from django.conf import settings

def test_redis_connection():
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        print("Successfully connected to Redis")
    except redis.ConnectionError:
        print("Failed to connect to Redis")

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'access_key_manager.settings')
    django.setup()
    test_redis_connection()