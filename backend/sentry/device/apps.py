"""Device app configuration."""

from django.apps import AppConfig


class DeviceConfig(AppConfig):
    """Device app configuration."""

    default_auto_field: str = "django.db.models.BigAutoField"
    name = "device"
