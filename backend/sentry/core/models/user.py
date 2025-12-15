"""User model."""

from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers.user_manager import UserManager


class User(AbstractUser):
    """Custom user model."""

    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, blank=True)  # Didn't know null is discouraged in Django
    last_name = models.CharField(max_length=255)
    profile_picture = models.ImageField(
        max_length=255,
        upload_to="user/images/profile_pictures/",
        blank=True,
    )

    # Override groups and user_permissions to avoid reverse accessor clashes
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="core_user_set",
        related_query_name="core_user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="core_user_set",
        related_query_name="core_user",
    )

    objects = UserManager()

    class Meta:  # noqa: D106
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering: ClassVar[list] = ["-id"]
        indexes: ClassVar[list] = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
        ]
