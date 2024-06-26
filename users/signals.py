import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from .models import User

logger = logging.getLogger(__name__)

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
        try:
            if instance.is_school_personnel:
                permission = Permission.objects.get(codename='can_purchase_access_key')
                instance.user_permissions.add(permission)
                logger.info(f"Assigned 'can_purchase_access_key' permission to user {instance.email}.")
            elif instance.is_admin:
                permission = Permission.objects.get(codename='can_revoke_access_key')
                instance.user_permissions.add(permission)
                logger.info(f"Assigned 'can_revoke_access_key' permission to admin user {instance.email}.")
        except Permission.DoesNotExist as e:
            logger.error(f"Permission assignment failed for user {instance.email}: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error while assigning permissions to user {instance.email}: {str(e)}")
    else:
        logger.info(f"User {instance.email} updated, but no permissions were assigned.")
