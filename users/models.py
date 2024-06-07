from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    is_school_personnel = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, blank=True, related_name='users')


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

    def __str__(self):
        return f"{self.user.email} - {self.payment_method}"
    