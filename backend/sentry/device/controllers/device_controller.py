"""Device endpoints (called by ESP32)."""

import logging

from django.http import HttpRequest
from ninja import Router

from device.schemas import DeviceDataRequest, DeviceDataResponse

device_router = Router(tags=["device"])


def receive_device_data(
    request: HttpRequest,  # noqa: ARG001
    payload: DeviceDataRequest,
) -> DeviceDataResponse:
    """Endpoint the embedded device can POST MPU6050 data to.

    URL (once wired into v1): /api/v1/device/data
    """
    # NOTE: plug into DB + ML pipeline later
    # For now we just log and acknowledge

    logger = logging.getLogger("device")
    logger.info(
        "Device data: %s, ax=%s, ay=%s, az=%s, roll=%s, pitch=%s, tilt_detected=%s",
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
