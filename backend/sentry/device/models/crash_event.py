"""Crash event model."""

from typing import ClassVar

from core.models import User
from django.db import models


class CrashEvent(models.Model):
    """Crash event model for storing crash detection events."""

    device_id = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    crash_timestamp = models.DateTimeField()
    is_confirmed_crash = models.BooleanField(default=False)  # pyright: ignore[reportArgumentType]
    confidence_score = models.FloatField(null=True, blank=True)
    severity = models.CharField(
        max_length=20,
        choices=[
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        default="low",
    )
    crash_type = models.CharField(max_length=255, blank=True)
    ai_reasoning = models.TextField(blank=True)
    key_indicators = models.JSONField(default=list, blank=True)
    false_positive_risk = models.FloatField(null=True, blank=True)
    max_g_force = models.FloatField(null=True, blank=True)
    impact_acceleration = models.JSONField(default=dict, blank=True)
    final_tilt = models.JSONField(default=dict, blank=True)
    # GPS Location at Crash Time
    crash_latitude = models.FloatField(null=True, blank=True)
    crash_longitude = models.FloatField(null=True, blank=True)
    crash_altitude = models.FloatField(null=True, blank=True)
    gps_fix_at_crash = models.BooleanField(default=False)  # pyright: ignore[reportArgumentType]
    satellites_at_crash = models.IntegerField(null=True, blank=True)
    alert_sent = models.BooleanField(default=False)  # pyright: ignore[reportArgumentType]
    user_feedback = models.CharField(
        max_length=20,
        choices=[
            ("true_positive", "True Positive"),
            ("false_positive", "False Positive"),
        ],
        blank=True,
    )
    user_comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # noqa: D106
        verbose_name = "Crash Event"
        verbose_name_plural = "Crash Events"
        ordering: ClassVar[list[str]] = ["-crash_timestamp"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["device_id", "-crash_timestamp"]),
            models.Index(fields=["is_confirmed_crash", "-crash_timestamp"]),
            models.Index(fields=["user", "-crash_timestamp"]),
        ]

    def __str__(self) -> str:  # noqa: D105
        return f"Crash event for {self.device_id} at {self.crash_timestamp}"
