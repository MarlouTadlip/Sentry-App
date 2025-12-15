"""Schemas for device data."""

from ninja import Schema


class DeviceDataRequest(Schema):
    """Basic MPU6050 payload from ESP32."""

    ax: float
    ay: float
    az: float
    roll: float
    pitch: float
    tilt_detected: bool  # true when tilt exceeds your threshold
    device_id: str | None = None
    timestamp: int | None = None  # optional unix ms


class DeviceDataResponse(Schema):
    """Basic response to device."""

    success: bool
    message: str
