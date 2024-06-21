from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from .models import User

@receiver(post_save, sender=User)
def assign_permissions(sender, instance, created, **kwargs):
    """
    Assigns permissions to users based on their roles (school personnel or admin).

    Args:
        sender: The model class (User).
        instance: The actual instance being saved.
        created: A boolean; True if a new record was created.
    """
    if created:
        if instance.is_school_personnel:
            permission = Permission.objects.get(codename='can_purchase_access_key')
            instance.user_permissions.add(permission)
        elif instance.is_admin:
            permission = Permission.objects.get(codename='can_revoke_access_key')
            instance.user_permissions.add(permission)
