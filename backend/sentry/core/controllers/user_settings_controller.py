"""User settings controller."""

import logging
from typing import Any

from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError

from core.models import UserSettings

logger = logging.getLogger("core")


def get_user_settings(request: HttpRequest) -> dict[str, Any]:
    """Get user's settings.

    Args:
        request: The HTTP request object

    Returns:
        Dictionary containing user settings

    Raises:
        HttpError: If settings retrieval fails

    """
    try:
        user = request.user  # pyright: ignore[reportAttributeAccessIssue]

        # Get or create user settings (create with defaults if doesn't exist)
        user_settings, created = UserSettings.objects.get_or_create(
            user=user,
            defaults={"crash_alert_interval_seconds": 15},
        )

        if created:
            logger.info(
                "[OK] Created default user settings for user_id=%s",
                user.id,  # pyright: ignore[reportAttributeAccessIssue]
            )

        return {
            "crash_alert_interval_seconds": user_settings.crash_alert_interval_seconds,
        }

    except Exception as e:
        logger.exception("Error retrieving user settings")
        raise HttpError(status_code=500, message="Failed to retrieve user settings") from e


def update_user_settings(
    request: HttpRequest,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Update user's settings.

    Args:
        request: The HTTP request object
        data: The settings update data (contains crash_alert_interval_seconds)

    Returns:
        Dictionary containing success message and updated settings

    Raises:
        HttpError: If settings update fails or validation fails

    """
    try:
        user = request.user  # pyright: ignore[reportAttributeAccessIssue]
        interval = data.get("crash_alert_interval_seconds")

        # Validate interval range
        if interval is None:
            raise HttpError(status_code=400, message="crash_alert_interval_seconds is required")

        if not isinstance(interval, int) or interval < 10 or interval > 60:
            raise HttpError(
                status_code=400,
                message="crash_alert_interval_seconds must be an integer between 10 and 60",
            )

        # Get or create user settings
        with transaction.atomic():  # type: ignore[call-overload]
            user_settings, created = UserSettings.objects.get_or_create(
                user=user,
                defaults={"crash_alert_interval_seconds": interval},
            )

            if not created:
                # Update existing settings
                user_settings.crash_alert_interval_seconds = interval
                user_settings.save()

            logger.info(
                "[OK] Updated user settings | user_id=%s | crash_alert_interval_seconds=%s",
                user.id,  # pyright: ignore[reportAttributeAccessIssue]
                interval,
            )

        return {
            "message": "User settings updated successfully",
            "crash_alert_interval_seconds": user_settings.crash_alert_interval_seconds,
        }

    except HttpError:
        raise
    except Exception as e:
        logger.exception("Error updating user settings")
        raise HttpError(status_code=500, message="Failed to update user settings") from e

