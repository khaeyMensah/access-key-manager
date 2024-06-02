import secrets
import string
from .models import AccessKey

def generate_access_key():
    key_length = 20
    characters = string.ascii_letters + string.digits

    while True:
        key = ''.join(secrets.choice(characters) for _ in range(key_length))
        if not AccessKey.objects.filter(key=key).exists():
            return key
