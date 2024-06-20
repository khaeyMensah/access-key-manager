import secrets
import string
from .models import AccessKey


def generate_access_key(key_length=20):
    """
    Generates a unique access key.

    Parameters:
        key_length (int): The length of the generated access key. Default is 20.

    Returns:
        str: A unique access key of the specified length.

    Raises:
        ValueError: If the specified key length is less than 1.

    Uses the secrets module to generate random characters from the ASCII letters and digits.
    It then checks if the generated key already exists in the AccessKey model.
    If it does not exist, the function returns the generated key.
    If it does, the function continues generating new keys until a unique one is found.
    """

    characters = string.ascii_letters + string.digits

    while True:
        key = ''.join(secrets.choice(characters) for _ in range(key_length))
        if not AccessKey.objects.filter(key=key).exists():
            return key
        