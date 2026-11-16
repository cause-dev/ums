from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends the default Django User model.
    """

    display_name = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
