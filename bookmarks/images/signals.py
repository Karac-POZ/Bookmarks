from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Image


@receiver(m2m_changed, sender=Image.users_like.through)
def users_like_changed(sender: str,
                       instance: Image,
                       **kwargs) -> None:
    """
    Handles changes to the users who like an image.

    When a user is added or removed from the list of likes for an image,
    this function updates the total_likes count and saves the updated image.

    Args:
        sender (str): The model that triggered the signal.
        instance (Image): The image whose likes were changed.

    Returns:
        None
    """
    instance.total_likes = instance.users_like.count()
    instance.save()
