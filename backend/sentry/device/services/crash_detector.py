"""Crash detector service for retrieving sensor data."""

import logging
from datetime import timedelta
from typing import Any

from django.utils import timezone

from device.models import SensorData

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

        except Exception:
            logger.exception("Error retrieving recent sensor data")
            return []
