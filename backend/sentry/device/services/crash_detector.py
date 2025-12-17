"""Crash detector service for retrieving sensor data."""

import logging
from datetime import timedelta
from typing import Any

from core.models import UserSettings
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.utils import timezone

from device.models import CrashEvent, SensorData
from device.schemas.crash_schema import GPSDataSchema

logger = logging.getLogger(__name__)


class CrashDetectorService:
    """Service for crash detection operations."""

    def get_recent_sensor_data(
        self,
        device_id: str,
        lookback_seconds: int = 30,
    ) -> list[dict[str, Any]]:
        """Get recent sensor data for a device.

        Args:
            device_id: Device identifier
            lookback_seconds: Number of seconds to look back

        Returns:
            List of sensor data dictionaries

        """
        try:
            # Calculate time threshold
            time_threshold = timezone.now() - timedelta(seconds=lookback_seconds)

            # Query recent sensor data
            sensor_data = (
                SensorData.objects.filter(  # pyright: ignore[reportAttributeAccessIssue]
                    device_id=device_id,
                    timestamp__gte=time_threshold,
                )
                .order_by("timestamp")
                .values(
                    "ax",
                    "ay",
                    "az",
                    "roll",
                    "pitch",
                    "tilt_detected",
                    "timestamp",
                )
            )

            # Convert to list of dicts with proper timestamp format
            return [
                {
                    "ax": float(data["ax"]),
                    "ay": float(data["ay"]),
                    "az": float(data["az"]),
                    "roll": float(data["roll"]),
                    "pitch": float(data["pitch"]),
                    "tilt_detected": bool(data["tilt_detected"]),
                    "timestamp": data["timestamp"].isoformat()
                    if hasattr(data["timestamp"], "isoformat")
                    else str(data["timestamp"]),
                }
                for data in sensor_data
            ]

        except DatabaseError:
            logger.exception("Error retrieving recent sensor data")
            return []

    def get_user_crash_alert_interval(self, user: User | None) -> int:
        """Get user's crash alert interval from UserSettings.

        Args:
            user: User object (may be None or unauthenticated)

        Returns:
            Crash alert interval in seconds (default: 15)

        """
        if not user or not hasattr(user, "is_authenticated") or not user.is_authenticated:
            return 15

        try:
            user_settings, _ = UserSettings.objects.get_or_create(  # type: ignore[attr-defined]
                user=user,
                defaults={"crash_alert_interval_seconds": 15},
            )
            interval = user_settings.crash_alert_interval_seconds
            logger.info(
                "[SETTINGS] Using crash alert interval=%s seconds (user_id=%s)",
                interval,
                user.id,  # pyright: ignore[reportAttributeAccessIssue]
            )
        except (DatabaseError, ValueError) as e:
            logger.warning(
                "[WARN] Failed to fetch user settings, using default interval: %s",
                e,
            )
            return 15
        else:
            return interval

    def get_recent_crash_events(
        self,
        device_id: str,
        user: User | None,
        lookback_seconds: int,
        num_events: int,
    ) -> list[dict[str, Any]]:
        """Get recent crash events for AI context.

        Args:
            device_id: Device identifier
            user: User object (may be None or unauthenticated)
            lookback_seconds: Number of seconds to look back
            num_events: Maximum number of events to retrieve

        Returns:
            List of crash event dictionaries

        """
        if not user or not hasattr(user, "is_authenticated") or not user.is_authenticated:
            return []

        try:
            time_threshold = timezone.now() - timedelta(seconds=lookback_seconds)
            recent_crash_events = (
                CrashEvent.objects.filter(  # type: ignore[attr-defined]
                    device_id=device_id,
                    crash_timestamp__gte=time_threshold,
                )
                .order_by("-crash_timestamp")[:num_events]
                .values(
                    "is_confirmed_crash",
                    "confidence_score",
                    "severity",
                    "crash_type",
                    "max_g_force",
                    "crash_timestamp",
                )
            )
            crash_events = list(recent_crash_events)
            logger.info(
                "[HISTORY] Retrieved %s recent crash events for AI context (device_id=%s, num_events=%s)",
                len(crash_events),
                device_id,
                num_events,
            )
        except DatabaseError as e:
            logger.warning(
                "[WARN] Failed to retrieve crash event history: %s",
                e,
            )
            return []
        else:
            return crash_events

    def extract_gps_data(self, gps_data: GPSDataSchema | None) -> dict[str, Any]:
        """Extract GPS data from request.

        Args:
            gps_data: GPS data from request (may be None)

        Returns:
            Dictionary with GPS fields (latitude, longitude, altitude, accuracy, speed, speed_change)

        """
        if not gps_data or not gps_data.latitude or not gps_data.longitude:
            return {
                "latitude": None,
                "longitude": None,
                "altitude": None,
                "accuracy": None,
                "speed": None,
                "speed_change": None,
            }

        return {
            "latitude": gps_data.latitude,
            "longitude": gps_data.longitude,
            "altitude": gps_data.altitude,
            "accuracy": gps_data.accuracy,
            "speed": gps_data.speed,  # Speed in m/s
            "speed_change": gps_data.speed_change,  # Speed change in m/s²
        }
