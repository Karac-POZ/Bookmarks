from django.contrib import admin

# Import the Action model from the current package (.models)
from .models import Action


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    """
    Custom admin interface for managing Actions.
    Attributes:
        list_display (list): Fields to display on the admin index page.
        list_filter (list): Fields to use as filters on the admin index page.
        search_fields (list): Fields to search when searching in the admin interface.
    Methods:
        None
    """

    # Define fields to display on the admin index page
    list_display = [
        'user',  # The user who performed the action
        'verb',  # The type of action performed (e.g., "liked", "commented")
        'target',  # The target object of the action (e.g., a post or comment)
        'created'  # The timestamp when the action was created
    ]

    # Define fields to use as filters on the admin index page
    list_filter = [
        'created'  # Filter actions by creation date
    ]

    # Define fields to search when searching in the admin interface
    search_fields = [
        'verb'  # Search for actions with specific verb (e.g., "like")
    ]
