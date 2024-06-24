from django.core.exceptions import ValidationError
from django.db import models
from users.models import School, User


# Create your models here.
def validate_active_key(access_key):
    """
    Validates that a school can have only one active access key at a time.

    Args:
        access_key (AccessKey): The AccessKey instance to be validated.

    Raises:
        ValidationError: If the school already has an active access key.
        
    Example:
        >>> key = AccessKey(school=school, status='active')
        >>> validate_active_key(key)
    """
    school = access_key.school
    active_keys = school.access_keys.filter(status='active')
    if active_keys.exists() and access_key.status == 'active':
        raise ValidationError('A school can have only one active access key at a time.')


class AccessKey(models.Model):
    """
    Model representing an access key for a school.

    Attributes:
        key (CharField): A unique identifier for the access key.
        school (ForeignKey):  References the school that this access key belongs to.
        status (CharField): The current status of the access key.
        assigned_to (ForeignKey): The user to whom this access key is assigned.
        procurement_date (DateField): The date when this access key was procured.
        expiry_date (DateField): The date when this access key expires.
        revoked_by (ForeignKey): The user who revoked this access key.
        revoked_on (DateTimeField): The date and time when this access key was revoked.
        price (DecimalField): The price of this access key.

    Methods:
        __str__(self): Returns a string representation of the access key.
    """
    key = models.CharField(max_length=20, unique=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='access_keys')
    status = models.CharField(max_length=10,
                               choices=[('active', 'Active'), ('expired', 'Expired'), ('revoked', 'Revoked')],
                               validators=[validate_active_key])

    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_keys')
    procurement_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField()
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='revoked_access_keys')
    revoked_on = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.key} - {self.school.name} - {self.status}"
    
    
class KeyLog(models.Model):
    """
    Model representing a log entry for an action performed on an access key.

    Attributes:
        action (CharField): A description of the action performed on the access key.
        user (ForeignKey): The user who performed the action.
        access_key (ForeignKey): The access key on which the action was performed.
        timestamp (DateTimeField): The timestamp when the action was performed.
    """

    action = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    access_key = models.ForeignKey(AccessKey, on_delete=models.CASCADE, related_name='key_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
