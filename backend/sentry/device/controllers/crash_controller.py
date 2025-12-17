"""Crash controller."""

import logging

from core.ai.gemini_service import GeminiService
from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError

from device.models import CrashEvent
from device.schemas.crash_schema import (
    CrashAlertRequest,
    CrashAlertResponse,
    CrashEventSchema,
    CrashFeedbackRequest,
    CrashFeedbackResponse,
)
from device.services.crash_detector import CrashDetectorService
from device.services.fcm_service import FCMService
from device.utils.crash_utils import notify_loved_ones_with_gps

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
        # Log incoming crash alert request
        gps_info = (
            f"GPS: lat={data.gps_data.latitude},"
            f"lng={data.gps_data.longitude},"
            f"accuracy={data.gps_data.accuracy}m,"
            f"speed={data.gps_data.speed}m/s"
            if data.gps_data and data.gps_data.latitude and data.gps_data.longitude
            else "GPS: no data"
        )
        logger.info(
            "[IN] Crash alert received | device_id=%s | timestamp=%s | "
            "threshold_severity=%s | trigger_type=%s | g_force=%.2fg | "
            "sensor: ax=%.2f, ay=%.2f, az=%.2f | roll=%.1f deg, pitch=%.1f deg | "
            "tilt_detected=%s | %s",
            data.device_id,
            data.timestamp,
            data.threshold_result.severity,
            data.threshold_result.trigger_type,
            data.threshold_result.g_force,
            data.sensor_reading.ax,
            data.sensor_reading.ay,
            data.sensor_reading.az,
            data.sensor_reading.roll,
            data.sensor_reading.pitch,
            data.sensor_reading.tilt_detected,
            gps_info,
        )

        # Initialize services
        gemini_service = GeminiService()
        crash_detector = CrashDetectorService()
        fcm_service = FCMService()

        # Fetch user's crash alert interval from UserSettings
        user = getattr(request, "user", None)
        crash_alert_interval = crash_detector.get_user_crash_alert_interval(user)

        # Calculate dynamic lookback seconds based on interval
        # Formula: min(30 + (interval - 10) * 3, 180)
        # Example: 10s interval = 30s lookback, 30s interval = 90s lookback, 60s interval = 180s lookback
        lookback_seconds = min(30 + (crash_alert_interval - 10) * 3, 180)
        logger.info(
            "[CONTEXT] Calculated lookback_seconds=%s based on interval=%s (device_id=%s)",
            lookback_seconds,
            crash_alert_interval,
            data.device_id,
        )

        # Retrieve recent sensor data with dynamic lookback
        recent_data = crash_detector.get_recent_sensor_data(
            device_id=data.device_id,
            lookback_seconds=lookback_seconds,
        )
        logger.info(
            "[DATA] Retrieved %s sensor data points for context (device_id=%s, lookback_seconds=%s)",
            len(recent_data),
            data.device_id,
            lookback_seconds,
        )

        # Retrieve recent crash events for AI context
        # Number of events: max(1, interval // 20)
        # Example: 10s interval = 1 event, 30s interval = 1 event, 60s interval = 3 events
        num_crash_events = max(1, crash_alert_interval // 20)
        crash_events = crash_detector.get_recent_crash_events(
            device_id=data.device_id,
            user=user,
            lookback_seconds=lookback_seconds,
            num_events=num_crash_events,
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

        # Call Gemini AI for analysis with crash event history
        logger.info(
            "[AI] Calling Gemini AI for crash analysis (device_id=%s, crash_events=%s)",
            data.device_id,
            len(crash_events),
        )
        ai_analysis = gemini_service.analyze_crash_data(
            sensor_data=recent_data,
            current_reading=current_reading,
            context_seconds=lookback_seconds,
            crash_events=crash_events,
        )
        logger.info(
            "[OK] AI analysis complete | device_id=%s | is_crash=%s | confidence=%.2f | "
            "severity=%s | crash_type=%s | false_positive_risk=%.2f | reasoning=%s...",
            data.device_id,
            ai_analysis["is_crash"],
            ai_analysis["confidence"],
            ai_analysis["severity"],
            ai_analysis["crash_type"],
            ai_analysis["false_positive_risk"],
            ai_analysis["reasoning"][:100],
        )

        # Create CrashEvent if confirmed
        crash_event = None
        if ai_analysis["is_crash"]:
            logger.info(
                "[CRASH] Crash confirmed by AI - creating CrashEvent (device_id=%s, severity=%s, confidence=%.2f)",
                data.device_id,
                ai_analysis["severity"],
                ai_analysis["confidence"],
            )
            with transaction.atomic():  # type: ignore[call-overload]
                # Extract GPS data if available
                gps_data = crash_detector.extract_gps_data(data.gps_data)
                if gps_data["latitude"] and gps_data["longitude"]:
                    logger.info(
                        "[GPS] GPS location available: (%s, %s) accuracy=%sm "
                        "speed=%.2fm/s speed_change=%.2fm/s² (device_id=%s)",
                        gps_data["latitude"],
                        gps_data["longitude"],
                        gps_data["accuracy"],
                        gps_data["speed"],
                        gps_data["speed_change"],
                        data.device_id,
                    )
                else:
                    logger.warning("[WARN] No GPS location available at crash time (device_id=%s)", data.device_id)

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
                    # GPS and speed fields
                    crash_latitude=gps_data["latitude"],
                    crash_longitude=gps_data["longitude"],
                    crash_altitude=gps_data["altitude"],
                    gps_accuracy_at_crash=gps_data["accuracy"],
                    speed_at_crash=gps_data["speed"],
                    speed_change_at_crash=gps_data["speed_change"],
                    max_speed_before_crash=None,  # Will be calculated from recent sensor data if available
                )
                logger.info(
                    "[SAVE] CrashEvent created successfully | crash_event_id=%s | device_id=%s | "
                    "severity=%s | confidence=%.2f",  # type: ignore[attr-defined]
                    crash_event.id,  # type: ignore[attr-defined]
                    data.device_id,
                    ai_analysis["severity"],
                    ai_analysis["confidence"],
                )

                # Send FCM push notification
                if ai_analysis["severity"] in ["high", "medium"]:
                    logger.info(
                        "[FCM] Sending FCM push notification (device_id=%s, severity=%s, crash_event_id=%s)",  # type: ignore[attr-defined]
                        data.device_id,
                        ai_analysis["severity"],
                        crash_event.id,  # type: ignore[attr-defined]
                    )
                    notification_sent = fcm_service.send_crash_notification(
                        device_id=data.device_id,
                        crash_event=crash_event,
                        ai_analysis=ai_analysis,
                    )
                    if notification_sent:
                        logger.info("[OK] FCM notification sent successfully (device_id=%s)", data.device_id)
                    else:
                        logger.warning("[WARN] FCM notification failed to send (device_id=%s)", data.device_id)

                    # Send GPS location to loved ones
                    logger.info(
                        "[LOVED_ONES] Notifying loved ones with GPS location (device_id=%s, crash_event_id=%s)",  # type: ignore[attr-defined]
                        data.device_id,
                        crash_event.id,  # type: ignore[attr-defined]
                    )
                    notify_loved_ones_with_gps(
                        device_id=data.device_id,
                        crash_event=crash_event,
                    )
        else:
            logger.info(
                "[OK] False positive detected by AI - no crash event created "
                "(device_id=%s, confidence=%.2f, false_positive_risk=%.2f)",
                data.device_id,
                ai_analysis["confidence"],
                ai_analysis["false_positive_risk"],
            )

        logger.info(
            "[OUT] Crash alert processing complete | device_id=%s | is_crash=%s | "
            "crash_event_created=%s | crash_event_id=%s",  # type: ignore[attr-defined]
            data.device_id,
            ai_analysis["is_crash"],
            crash_event is not None,
            crash_event.id if crash_event else None,  # type: ignore[attr-defined]
        )

        return CrashAlertResponse(
            is_crash=ai_analysis["is_crash"],
            confidence=ai_analysis["confidence"],
            severity=ai_analysis["severity"],
            crash_type=ai_analysis["crash_type"],
            reasoning=ai_analysis["reasoning"],
            key_indicators=ai_analysis["key_indicators"],
            false_positive_risk=ai_analysis["false_positive_risk"],
            crash_event_id=crash_event.id if crash_event else None,  # type: ignore[attr-defined]
        )

    except Exception:
        logger.exception("Error processing crash alert")
        raise HttpError(status_code=500, message="Failed to process crash alert") from None


def submit_crash_feedback(
    _request: HttpRequest,
    event_id: int,
    data: CrashFeedbackRequest,
) -> CrashFeedbackResponse:
    """Submit user feedback for a crash event.

    Args:
        request: HTTP request object
        event_id: Crash event ID
        data: Feedback data (user_feedback, user_comments)

    Returns:
        Feedback response

    Raises:
        HttpError: If event not found or invalid feedback

    """
    # Get crash event
    crash_event = CrashEvent.objects.filter(id=event_id).first()  # type: ignore[attr-defined]
    if not crash_event:
        logger.warning("[WARN] Crash event not found (event_id=%s)", event_id)
        raise HttpError(status_code=404, message="Crash event not found")

    # Validate feedback value
    if data.user_feedback not in ["true_positive", "false_positive"]:
        logger.warning(
            "[WARN] Invalid feedback value (event_id=%s, feedback=%s)",
            event_id,
            data.user_feedback,
        )
        raise HttpError(
            status_code=400,
            message="Invalid feedback value. Must be 'true_positive' or 'false_positive'",
        )

    try:
        # Update crash event with feedback
        crash_event.user_feedback = data.user_feedback  # type: ignore[attr-defined]
        if data.user_comments:
            crash_event.user_comments = data.user_comments  # type: ignore[attr-defined]
        crash_event.save()  # type: ignore[attr-defined]

        logger.info(
            "[OK] User feedback submitted (event_id=%s, feedback=%s)",
            event_id,
            data.user_feedback,
        )

        return CrashFeedbackResponse(
            success=True,
            message="Feedback submitted successfully",
        )

    except HttpError:
        raise
    except Exception:
        logger.exception("Error submitting crash feedback")
        raise HttpError(status_code=500, message="Failed to submit feedback") from None


def get_crash_events(
    request: HttpRequest,
    device_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[CrashEventSchema]:
    """Get crash events for a device or user.

    Args:
        request: HTTP request object
        device_id: Optional device ID filter
        limit: Maximum number of events to return
        offset: Offset for pagination

    Returns:
        List of crash events

    """
    try:
        queryset = CrashEvent.objects.all()  # type: ignore[attr-defined]

        # Filter by device_id if provided
        if device_id:
            queryset = queryset.filter(device_id=device_id)

        # Filter by user if authenticated (using getattr for type safety)
        user = getattr(request, "user", None)
        if user and hasattr(user, "is_authenticated") and user.is_authenticated:
            queryset = queryset.filter(user=user)  # type: ignore[attr-defined]

        # Order by crash_timestamp descending (most recent first)
        queryset = queryset.order_by("-crash_timestamp")

        # Apply pagination
        events = queryset[offset : offset + limit]

        # Convert to schema
        event_schemas = [
            CrashEventSchema(
                id=event.id,  # type: ignore[attr-defined]
                device_id=event.device_id,  # type: ignore[attr-defined]
                crash_timestamp=event.crash_timestamp.isoformat(),  # type: ignore[attr-defined]
                is_confirmed_crash=event.is_confirmed_crash,  # type: ignore[attr-defined]
                confidence_score=event.confidence_score,  # type: ignore[attr-defined]
                severity=event.severity,  # type: ignore[attr-defined]
                crash_type=event.crash_type,  # type: ignore[attr-defined]
                ai_reasoning=event.ai_reasoning,  # type: ignore[attr-defined]
                key_indicators=event.key_indicators or [],  # type: ignore[attr-defined]
                false_positive_risk=event.false_positive_risk,  # type: ignore[attr-defined]
                max_g_force=event.max_g_force,  # type: ignore[attr-defined]
                crash_latitude=event.crash_latitude,  # type: ignore[attr-defined]
                crash_longitude=event.crash_longitude,  # type: ignore[attr-defined]
                crash_altitude=event.crash_altitude,  # type: ignore[attr-defined]
                gps_accuracy_at_crash=event.gps_accuracy_at_crash,  # type: ignore[attr-defined]
                speed_at_crash=event.speed_at_crash,  # type: ignore[attr-defined]
                speed_change_at_crash=event.speed_change_at_crash,  # type: ignore[attr-defined]
                max_speed_before_crash=event.max_speed_before_crash,  # type: ignore[attr-defined]
                user_feedback=event.user_feedback or None,  # type: ignore[attr-defined]
                user_comments=event.user_comments or None,  # type: ignore[attr-defined]
                created_at=event.created_at.isoformat(),  # type: ignore[attr-defined]
                updated_at=event.updated_at.isoformat(),  # type: ignore[attr-defined]
            )
            for event in events
        ]

        logger.info(
            "[OK] Retrieved %s crash events (device_id=%s, limit=%s, offset=%s)",
            len(event_schemas),
            device_id,
            limit,
            offset,
        )
    except Exception:
        logger.exception("Error retrieving crash events")
        raise HttpError(status_code=500, message="Failed to retrieve crash events") from None
    else:
        return event_schemas
