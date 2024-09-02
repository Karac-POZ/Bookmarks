from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Image(models.Model):
    """
    Model for an image.
    Attributes:
        user (User): The user who created the image.
        title (str): The title of the image.
        slug (str): A unique slug for the image.
        url (str): The URL of the image.
        image (ImageField): The actual image file.
        description (str): A brief description of the image.
        created (datetime): The date and time the image was created.
        users_like (ManyToManyField): Users who have liked the image.
        total_likes (int): The total number of likes for the image.
    Methods:
        __str__(): Returns a string representation of the image.
        save(): Saves the image to the database.
        get_absolute_url(): Returns the absolute URL of the image.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='images_created',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    users_like = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='images_liked',
        blank=True,
    )
    total_likes = models.PositiveIntegerField(default=0)

    class Meta:
        """
        Metadata for the Image model.
        Attributes:
            indexes (list): A list of database indexes to create.
            ordering (str): The default ordering for the image queryset.
        """
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['-total_likes'])
        ]
        ordering = ['-created']

    def __str__(self):
        """
        Returns a string representation of the image.
        Returns:
            str: The title of the image.
        """
        return self.title

    def save(self, *args, **kwargs):
        """
        Saves the image to the database.
        If the slug is not set, it will be generated from the title.
        Args:
            *args: Variable arguments.
            **kwargs: Keyword arguments.
        Returns:
            None
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the absolute URL of the image.
        Args:
            *args: Variable arguments.
        Returns:
            str: The absolute URL of the image.
        """
        return reverse('images:detail', args=[self.id, self.slug])
