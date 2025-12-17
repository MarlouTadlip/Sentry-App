"""Crash controller."""

import logging

from core.ai.gemini_service import GeminiService
from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError

from device.models import CrashEvent
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse
from device.services.crash_detector import CrashDetectorService
from device.services.fcm_service import FCMService

logger = logging.getLogger("device")


def process_crash_alert(
    request: HttpRequest,
    data: CrashAlertRequest,
) -> CrashAlertResponse:
    """Process crash alert from mobile app (Tier 1 trigger).

    Flow:
    1. Receive threshold alert from mobile app
    2. Retrieve recent sensor data context
    3. Call Gemini AI for analysis
    4. Create CrashEvent if confirmed
    5. Send FCM push notification

    Args:
        request: HTTP request object
        data: Crash alert request data

    Returns:
        Crash alert response with AI analysis

    Raises:
        HttpError: If processing fails

    """
    try:
        # Initialize services
        gemini_service = GeminiService()
        crash_detector = CrashDetectorService()
        fcm_service = FCMService()

        # Retrieve recent sensor data (last 30 seconds)
        recent_data = crash_detector.get_recent_sensor_data(
            device_id=data.device_id,
            lookback_seconds=30,
        )

        # Prepare current reading dict
        current_reading = {
            "ax": data.sensor_reading.ax,
            "ay": data.sensor_reading.ay,
            "az": data.sensor_reading.az,
            "roll": data.sensor_reading.roll,
            "pitch": data.sensor_reading.pitch,
            "tilt_detected": data.sensor_reading.tilt_detected,
        }

        # Call Gemini AI for analysis
        ai_analysis = gemini_service.analyze_crash_data(
            sensor_data=recent_data,
            current_reading=current_reading,
            context_seconds=30,
        )

        # Create CrashEvent if confirmed
        crash_event = None
        if ai_analysis["is_crash"]:
            with transaction.atomic():  # type: ignore[call-overload]
                crash_event = CrashEvent.objects.create(  # type: ignore[attr-defined]
                    device_id=data.device_id,
                    user=request.user if hasattr(request, "user") and request.user.is_authenticated else None,  # type: ignore[attr-defined]
                    crash_timestamp=data.timestamp,
                    is_confirmed_crash=True,
                    confidence_score=ai_analysis["confidence"],
                    severity=ai_analysis["severity"],
                    crash_type=ai_analysis["crash_type"],
                    ai_reasoning=ai_analysis["reasoning"],
                    key_indicators=ai_analysis["key_indicators"],
                    false_positive_risk=ai_analysis["false_positive_risk"],
                    max_g_force=data.threshold_result.g_force,
                    impact_acceleration={
                        "ax": data.sensor_reading.ax,
                        "ay": data.sensor_reading.ay,
                        "az": data.sensor_reading.az,
                    },
                    final_tilt={
                        "roll": data.sensor_reading.roll,
                        "pitch": data.sensor_reading.pitch,
                    },
                )

                # Send FCM push notification
                if ai_analysis["severity"] in ["high", "medium"]:
                    fcm_service.send_crash_notification(
                        device_id=data.device_id,
                        crash_event=crash_event,
                        ai_analysis=ai_analysis,
                    )

        return CrashAlertResponse(
            is_crash=ai_analysis["is_crash"],
            confidence=ai_analysis["confidence"],
            severity=ai_analysis["severity"],
            crash_type=ai_analysis["crash_type"],
            reasoning=ai_analysis["reasoning"],
            key_indicators=ai_analysis["key_indicators"],
            false_positive_risk=ai_analysis["false_positive_risk"],
        )

    except Exception:
        logger.exception("Error processing crash alert")
        raise HttpError(status_code=500, message="Failed to process crash alert") from None
