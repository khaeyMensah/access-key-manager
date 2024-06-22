from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    A custom token generator for account activation.

    This class inherits from Django's built-in `PasswordResetTokenGenerator`
    and can be used to generate tokens for account activation.
    """
    pass

account_activation_token = AccountActivationTokenGenerator()
