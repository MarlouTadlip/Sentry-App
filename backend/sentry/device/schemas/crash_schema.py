"""Crash detection schemas."""

from ninja import Schema


class GPSDataSchema(Schema):
    """GPS data schema."""

    latitude: float | None
    longitude: float | None
    altitude: float | None
    accuracy: float | None  # GPS accuracy in meters
    speed: float | None  # Speed in m/s (calculated from GPS)
    speed_change: float | None  # Speed change in m/s² (sudden deceleration)
    timestamp: str


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
    gps_data: GPSDataSchema | None = None  # Optional GPS data (may not have fix at crash time)


class CrashAlertResponse(Schema):
    """Response schema for crash alert analysis."""

    is_crash: bool
    confidence: float
    severity: str
    crash_type: str
    reasoning: str
    key_indicators: list[str]
    false_positive_risk: float
    crash_event_id: int | None = None  # ID of created crash event (if any)


class CrashEventSchema(Schema):
    """Crash event schema for API responses."""

    id: int
    device_id: str
    crash_timestamp: str
    is_confirmed_crash: bool
    confidence_score: float | None
    severity: str
    crash_type: str
    ai_reasoning: str
    key_indicators: list[str]
    false_positive_risk: float | None
    max_g_force: float | None
    crash_latitude: float | None
    crash_longitude: float | None
    crash_altitude: float | None
    gps_accuracy_at_crash: float | None
    speed_at_crash: float | None
    speed_change_at_crash: float | None
    max_speed_before_crash: float | None
    user_feedback: str | None
    user_comments: str | None
    created_at: str
    updated_at: str


class CrashFeedbackRequest(Schema):
    """Request schema for user feedback on crash events."""

    user_feedback: str  # 'true_positive' or 'false_positive'
    user_comments: str | None = None


class CrashFeedbackResponse(Schema):
    """Response schema for crash feedback submission."""

    success: bool
    message: str
