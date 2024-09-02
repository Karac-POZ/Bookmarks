from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model


class Profile(models.Model):
    """
    User profile model.

    Attributes:
        user (OneToOneField): Foreign key to the User model.
        date_of_birth (DateField): Date of birth, can be null.
        photo (ImageField): Profile picture, can be blank.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='users/%Y/%m/%d',
        blank=True
    )

    def __str__(self):
        """
        Returns a string representation of the profile.

        Returns:
            str: Profile information as a string.
        """
        return f'Profile of {self.user.username}'


class Contact(models.Model):
    """
    Model for contact between two users.

    Attributes:
        user_from (ForeignKey): Foreign key to the User model, related_name is set to 'rel_from_set'.
        user_to (ForeignKey): Foreign key to the User model, related_name is set to 'rel_to_set'.
        created (DateTimeField): Date and time when the contact was made.
    """
    user_from = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rel_from_set',
        on_delete=models.CASCADE,
    )
    user_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rel_to_set',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Metadata for the Contact model.

        Attributes:
            indexes (list): List of indexes, in this case an index is created on the 'created' field.
            ordering (list): Ordering of the contacts based on the 'created' field.
        """
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def __str__(self):
        """
        Returns a string representation of the contact.

        Returns:
            str: Contact information as a string.
        """
        return f'{self.user_from} follows {self.user_to}'


# Add following field to User dynamically
user_model = get_user_model()
user_model.add_to_class(
    'following',
    models.ManyToManyField(
        'self',
        through=Contact,
        related_name='followers',
        symmetrical=False,
    ),
)
