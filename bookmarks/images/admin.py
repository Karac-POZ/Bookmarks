from django.contrib import admin
from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    """
    Custom admin interface for the Image model.
    Attributes:
        list_display (list): List of fields to display in the admin interface.
        list_filter (list): List of fields to filter by in the admin interface.
    """

    # Fields to display in the admin interface
    list_display = ['title', 'slug', 'image', 'created']

    # Fields to filter by in the admin interface
    list_filter = ['created']
