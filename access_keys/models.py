from django.core.exceptions import ValidationError
from django.db import models
from users.models import School, User


# Create your models here.
def validate_active_key(access_key):
    school = access_key.school
    active_keys = school.access_keys.filter(status='active')
    if active_keys.exists() and access_key.status == 'active':
        raise ValidationError('A school can have only one active access key at a time.')


class AccessKey(models.Model):
    key = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='access_keys')
    status = models.CharField(max_length=10, choices=[
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked')
    ], validators=[validate_active_key])
    
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_keys')
    procurement_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_access_keys')
    revoked_on = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.key} - {self.school.name} - {self.status}"


class KeyLog(models.Model):
    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_key = models.ForeignKey(AccessKey, on_delete=models.CASCADE, related_name='key_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
