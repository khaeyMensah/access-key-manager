from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Role(models.Model):
    name = models.CharField(max_length=255)

class User(AbstractUser):
    roles = models.ManyToManyField(Role)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

class BillingInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=255)
    billing_address = models.CharField(max_length=255)
    
