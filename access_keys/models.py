from django.db import models
from users.models import User

# Create your models here.
class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

class AccessKey(models.Model):
    key = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    date_of_procurement = models.DateField()
    expiry_date = models.DateField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

class RevokedAccessKey(models.Model):
    access_key = models.OneToOneField(AccessKey, on_delete=models.CASCADE)
    revoked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_revoked = models.DateTimeField()

class AuditLog(models.Model):
    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)