"""Device endpoints (called by ESP32)."""

import logging

from django.http import HttpRequest
from django.utils import timezone
from ninja import Router

from device.models import SensorData
from device.schemas import DeviceDataRequest, DeviceDataResponse

device_router = Router(tags=["device"])

logger = logging.getLogger("device")


def receive_device_data(
    request: HttpRequest,  # noqa: ARG001
    payload: DeviceDataRequest,
) -> DeviceDataResponse:
    """Endpoint the embedded device can POST MPU6050 data to.

    URL (once wired into v1): /api/v1/device/data
    """
    try:
        # Save sensor data to database
        SensorData.objects.create(  # type: ignore[attr-defined]
            device_id=payload.device_id or "unknown",
            ax=payload.ax,
            ay=payload.ay,
            az=payload.az,
            roll=payload.roll,
            pitch=payload.pitch,
            tilt_detected=payload.tilt_detected,
            timestamp=timezone.now(),
        )

        logger.info(
            "Device data saved: %s, ax=%s, ay=%s, az=%s, roll=%s, pitch=%s, tilt_detected=%s",
            payload.device_id,
            payload.ax,
            payload.ay,
            payload.az,
            payload.roll,
            payload.pitch,
            payload.tilt_detected,
        )

        return DeviceDataResponse(
            success=True,
            message="Data received",
        )
    except Exception:
        logger.exception("Error saving device data")
        return DeviceDataResponse(
            success=False,
            message="Failed to save data",
        )
