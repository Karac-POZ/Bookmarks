"""
Registers Profile model in Django Admin.

This class configures the Profile model to be displayed and editable through Django's admin interface.
"""

from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Configuration for Profile model in Django Admin.

    Attributes:
        list_display (list): Fields to display on the profile list page.
        raw_id_fields (list): Fields to display as raw ID fields.
    """

    list_display = ['user', 'date_of_birth', 'photo']
    raw_id_fields = ['user']
