from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model that extends AbstractUser with additional fields.

    Attributes:
        is_school_personnel (BooleanField): Indicates if the user is a school personnel.
        is_admin (BooleanField): Indicates if the user is an admin.
        school (ForeignKey): References the school the user is associated with.
        staff_id (CharField): The staff ID of the admin user.

    Methods:
        clean(self):
            Raises a ValidationError if the user is a school personnel and tries to change their school after submitting their profile.

        is_profile_complete(self):
            Returns True if the user's profile is complete, i.e., they have a first name, last name, email, and either are an admin or a school personnel with a school affiliation.
    """
    is_school_personnel = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    staff_id = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        permissions = [
            ("can_purchase_access_key", "Can purchase access key"),
            ("can_revoke_access_key", "Can revoke access key"),
        ]

    def clean(self):
        """
        Ensures that school personnel cannot change their school after submitting their profile.

        Args:
            self: The User instance.

        Raises:
            ValidationError: If the user is a school personnel and tries to change their school after submitting their profile.
        """
        if self.pk and self.is_profile_complete() and User.objects.filter(pk=self.pk, is_school_personnel=True, school__isnull=False).exists():
            old_school = User.objects.get(pk=self.pk).school
            if old_school != self.school:
                raise ValidationError("School personnel cannot change their school after submitting their profile.")

    def is_profile_complete(self):
        """
        Checks if the user's profile is complete.

        For admin users: checks for first name, last name, email, and staff_id.
        For school personnel: checks for first name, last name, email, and school affiliation.

        Returns:
            bool: True if the user's profile is complete, False otherwise.
        """
        base_check = bool(self.first_name and self.last_name and self.email)
        if self.is_admin:
            return base_check and bool(self.staff_id)
        elif self.is_school_personnel:
            return base_check and bool(self.school)
        return False  # For users who are neither admin nor school personnel


class School(models.Model):
    """
    Model representing a school.

    Attributes:
        name (CharField): The name of the school.

    Methods:
        __str__(self): Returns a string representation of the school, which is its name.
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BillingInformation(models.Model):
    """
    Model representing the billing information of a user.

    Attributes:
        user (OneToOneField): References the user associated with the billing information.
        payment_method (CharField): The method of payment (either MTN Mobile Money or Credit/Debit Card).
        mobile_money_number (CharField): The mobile money number for MTN Mobile Money payments.
        card_number (CharField): The card number for Credit/Debit Card payments.
        card_expiry (CharField): The expiry date of the card for Credit/Debit Card payments.
        card_cvv (CharField): The CVV code of the card for Credit/Debit Card payments.

    Methods:
        clean(self): Validates the billing information based on the selected payment method.
        __str__(self): Returns a string representation of the billing information, which is the user's email and payment method.
    """
    PAYMENT_METHODS = [
        ('mtn_momo', 'MTN Mobile Money'),
        ('card', 'Credit/Debit Card'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='billing_information')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    mobile_money_number = models.CharField(max_length=15, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    card_expiry = models.CharField(max_length=5, blank=True, null=True)
    card_cvv = models.CharField(max_length=4, null=True, blank=True)

    def clean(self):
        """
        Validates the billing information based on the selected payment method.
        """
        if self.payment_method == 'card':
            if not self.card_number or not self.card_expiry or not self.card_cvv:
                raise ValidationError('Card details are required for "Card" payment.')
            if self.mobile_money_number:
                raise ValidationError('Mobile money number should be empty for "Card" payment.')
        elif self.payment_method == 'mtn_momo':
            if not self.mobile_money_number:
                raise ValidationError('Mobile money number is required for "MOMO" payment.')
            if self.card_number or self.card_expiry or self.card_cvv:
                raise ValidationError('Card details should be empty for "MOMO" payment.')

    def __str__(self):
        return f"{self.user.email} - {self.get_payment_method_display()}"

