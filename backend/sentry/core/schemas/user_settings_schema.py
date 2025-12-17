"""User settings schema."""

from ninja import Schema
from pydantic import field_validator


class UserSettingsSchema(Schema):
    """User settings schema."""

    crash_alert_interval_seconds: int


class UserSettingsUpdateRequest(Schema):
    """User settings update request schema."""

    crash_alert_interval_seconds: int

    @field_validator("crash_alert_interval_seconds")
    @classmethod
    def validate_interval(cls, v: int) -> int:
        """Validate crash alert interval is within range.

        Args:
            v: The interval value

        Returns:
            The validated interval value

        Raises:
            ValueError: If interval is outside 10-60 range

        """
        if v < 10 or v > 60:
            raise ValueError("crash_alert_interval_seconds must be between 10 and 60")
        return v

