from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    pass

account_activation_token = AccountActivationTokenGenerator()




# from django.contrib.auth.tokens import PasswordResetTokenGenerator

# class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
#     """
#     A custom token generator for account activation.

#     This class inherits from Django's built-in `PasswordResetTokenGenerator` and can be used to generate tokens for account activation.

#     Attributes:
#         method (str): The method used to generate the token. Defaults to 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/'.
#         salt_size (int): The size of the salt used in the token generation. Defaults to 50.

#     Methods:
#         __call__(self, user_id, timestamp=None, single_use=False):
#             Generate a token for account activation.

#             Args:
#                 user_id (int): The ID of the user for whom the token is being generated.
#                 timestamp (int, optional): The timestamp to be included in the token. Defaults to the current timestamp.
#                 single_use (bool, optional): Whether the token should be single-use. Defaults to False.

#             Returns:
#                 str: The generated token for account activation.
#     """

#     def __call__(self, user_id, timestamp=None, single_use=False):
#         """
#         Generate a token for account activation.

#         Args:
#             user_id (int): The ID of the user for whom the token is being generated.
#             timestamp (int, optional): The timestamp to be included in the token. Defaults to the current timestamp.
#             single_use (bool, optional): Whether the token should be single-use. Defaults to False.

#         Returns:
#             str: The generated token for account activation.
#         """
#         return super().__call__(user_id, timestamp, single_use)