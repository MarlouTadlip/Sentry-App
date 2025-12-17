"""Crash detection schemas."""

from ninja import Schema


class SensorReading(Schema):
    """Sensor reading from device."""

    device_id: str
    ax: float
    ay: float
    az: float
    roll: float
    pitch: float
    tilt_detected: bool
    timestamp: str


class ThresholdResult(Schema):
    """Threshold detection result from client."""

    is_triggered: bool
    trigger_type: str | None  # 'g_force', 'tilt', 'both', or None
    severity: str  # 'low', 'medium', 'high'
    g_force: float
    tilt: dict
    timestamp: int


class CrashAlertRequest(Schema):
    """Request schema for crash alert from mobile app."""

    device_id: str
    sensor_reading: SensorReading
    threshold_result: ThresholdResult
    timestamp: str


class CrashAlertResponse(Schema):
    """Response schema for crash alert analysis."""

    is_crash: bool
    confidence: float
    severity: str
    crash_type: str
    reasoning: str
    key_indicators: list[str]
    false_positive_risk: float

