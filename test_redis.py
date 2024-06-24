import redis
from django.conf import settings

def test_redis_connection():
    """
    This function tests the connection to the Redis server using the provided URL in the Django settings.

    Parameters:
    None

    Returns:
    None

    Raises:
    redis.ConnectionError: If the connection to the Redis server fails.

    Example:
    ```
    test_redis_connection()
    ```

    """
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