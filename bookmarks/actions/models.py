from django.db import models  # Import the Django database model library
# Import the generic foreign key field from Django's content types framework
from django.contrib.contenttypes.fields import GenericForeignKey
# Import the content type model from Django's content types framework
from django.contrib.contenttypes.models import ContentType
from django.conf import settings  # Import the Django project settings


class Action(models.Model):
    """
    Represents an action performed by a user.
    Attributes:
        user (ForeignKey): The user who performed the action.
        verb (CharField): A brief description of the action (e.g., "liked", "commented").
        created (DateTimeField): The timestamp when the action was created.
        target_ct (ForeignKey): The content type of the target object.
        target_id (PositiveIntegerField): The ID of the target object.
        target (GenericForeignKey): A reference to the target object, using its content type and ID.
    Methods:
        None
    """
    # Define a foreign key to the user who performed the action
    user = models.ForeignKey(
        # Use the AUTH_USER_MODEL setting from Django's project settings
        settings.AUTH_USER_MODEL,
        related_name='actions',  # Use 'actions' as the related name for the foreign key
        on_delete=models.CASCADE  # Cascade delete actions when the user is deleted
    )
    # Define a character field to store the verb of the action (e.g., "liked", "commented")
    verb = models.CharField(max_length=255)
    # Define a datetime field to store the timestamp when the action was created
    created = models.DateTimeField(auto_now_add=True)
    # Define a foreign key to the content type of the target object
    target_ct = models.ForeignKey(
        ContentType,  # Use the ContentType model from Django's content types framework
        blank=True,
        null=True,
        related_name='target_obj',  # Use 'target_obj' as the related name for the foreign key
        on_delete=models.CASCADE  # Cascade delete actions when the target object is deleted
    )
    # Define a positive integer field to store the ID of the target object
    target_id = models.PositiveIntegerField(null=True, blank=True)
    # Define a generic foreign key to reference the target object using its content type and ID
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        """
        Metadata for the Action model.
        Attributes:
            indexes (list): A list of database indexes to create.
            ordering (list): The default order for retrieving actions from the database.
        Methods:
            None
        """
        # Define a database index on the '-created' field
        indexes = [
            models.Index(fields=['-created']),
            # Define a composite database index on 'target_ct' and 'target_id'
            models.Index(fields=['target_ct', 'target_id'])
        ]
        # Define the default order for retrieving actions from the database (by creation date in descending order)
        ordering = ['-created']
