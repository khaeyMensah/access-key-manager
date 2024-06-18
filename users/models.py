from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_school_personnel = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    staff_id = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        permissions = [
            ("can_purchase_access_key", "Can purchase access key"),
            ("can_revoke_access_key", "Can revoke access key"),
        ]
    
class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class BillingInformation(models.Model):
    PAYMENT_METHODS = [
        ('MTN', 'MTN Mobile Money'),
        ('Card', 'Credit/Debit Card'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='billing_information')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS)
    mobile_money_number = models.CharField(max_length=15, blank=True, null=True)
    card_number = models.CharField(max_length=20, blank=True, null=True)
    card_expiry = models.DateField(null=True, blank=True)
    card_cvv = models.CharField(max_length=4, null=True, blank=True)

    def clean(self):
        if self.payment_method == 'Card':
            if not self.card_number or not self.card_expiry or not self.card_cvv:
                raise ValidationError('Card details are required for payment method "Card".')
            if self.mobile_money_number:
                raise ValidationError('Mobile money number should be empty for payment method "Card".')
        elif self.payment_method == 'MTN':
            if not self.mobile_money_number:
                raise ValidationError('Mobile money number is required for payment method "MTN".')
            if self.card_number or self.card_expiry or self.card_cvv:
                raise ValidationError('Card details should be empty for payment method "MTN".')

    def __str__(self):
        return f"{self.user.email} - {self.get_payment_method_display()}"
