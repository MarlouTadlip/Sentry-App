"""Device token model for FCM push notifications."""

from typing import ClassVar

from core.models import User
from django.db import models


class DeviceToken(models.Model):
    """Device token model for storing FCM tokens."""

    device_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fcm_token = models.CharField(max_length=500)
    platform = models.CharField(
        max_length=20,
        choices=[
            ("ios", "iOS"),
            ("android", "Android"),
        ],
    )
    is_active = models.BooleanField(default=True)  # pyright: ignore[reportArgumentType]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # noqa: D106
        verbose_name = "Device Token"
        verbose_name_plural = "Device Tokens"
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["device_id"]),
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["fcm_token"]),
        ]
        unique_together: ClassVar[list[str]] = ["device_id", "fcm_token"]

    def __str__(self) -> str:  # noqa: D105
        return f"Device token for {self.device_id} ({self.platform})"
