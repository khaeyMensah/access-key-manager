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
    
    def clean(self):
        if self.pk and self.is_profile_complete() and User.objects.filter(pk=self.pk, is_school_personnel=True, school__isnull=False).exists():
            old_school = User.objects.get(pk=self.pk).school
            if old_school != self.school:
                raise ValidationError("School personnel cannot change their school after submitting their profile.")

    def is_profile_complete(self):
        return bool(self.first_name and self.last_name and self.email and 
                    (self.is_admin or (self.is_school_personnel and self.school)))
    


class School(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class BillingInformation(models.Model):
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
