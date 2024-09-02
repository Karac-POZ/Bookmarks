import requests
from django import forms
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Image


class ImageCreateForm(forms.ModelForm):
    """
    Custom form for creating new images.
    Attributes:
        title (str): The title of the image.
        url (str): The URL of the image.
        description (str): A brief description of the image.
    Returns:
        Image: A new Image instance with the saved data.
    """

    class Meta:
        """
        Metadata for the form.
        Attributes:
            model (Image): The model associated with this form.
            fields (list): The fields to include in the form.
            widgets (dict): The widgets to use for each field.
        """
        model = Image
        fields = ['title', 'url', 'description']
        widgets = {
            'url': forms.HiddenInput,
        }

    def clean_url(self):
        """
        Clean and validate the URL.
        Args:
            url (str): The URL to clean and validate.
        Returns:
            str: The cleaned and validated URL.
        Raises:
            forms.ValidationError: If the given URL does not match valid image extensions.
        """
        # Get the URL from the form data
        url = self.cleaned_data['url']

        # Valid image extensions
        valid_extensions = ['jpg', 'jpeg', 'png']

        # Extract the file extension from the URL
        extension = url.rsplit('.', 1)[1].lower()

        # Validate the file extension
        if extension not in valid_extensions:
            raise forms.ValidationError(
                'The given URL does not match valid image extensions.'
            )

        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        """
        Save the form data to a new Image instance.
        Args:
            force_insert (bool): Whether to insert the record even if it already exists.
            force_update (bool): Whether to update the record even if it does not exist.
            commit (bool): Whether to save the changes to the database.
        Returns:
            Image: The saved Image instance.
        """
        # Save the form data to a new Image instance
        image = super().save(commit=False)

        # Get the URL from the form data
        image_url = self.cleaned_data['url']

        # Extract the title and file extension from the URL
        name = slugify(image.title)
        extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{extension}'

        # Download the image from the given URL
        response = requests.get(image_url)

        # Save the image to the Image instance
        image.image.save(
            image_name,
            ContentFile(response.content),
            save=False
        )

        # Commit the changes to the database if required
        if commit:
            image.save()

        return image
