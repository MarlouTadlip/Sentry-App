"""User settings model."""

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from core.models import User


class UserSettings(models.Model):
    """User settings model for storing user preferences."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="settings",
    )
    crash_alert_interval_seconds = models.IntegerField(
        default=15,
        validators=[MinValueValidator(10), MaxValueValidator(60)],
        help_text="Minimum time between crash alert API calls (10-60 seconds)",
    )

    class Meta:
        verbose_name = "User Settings"
        verbose_name_plural = "User Settings"
        indexes = [
            models.Index(fields=["user"]),
        ]

    def __str__(self) -> str:
        return f"Settings for {self.user.email}"

