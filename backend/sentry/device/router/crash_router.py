"""Crash router."""

import logging

from django.http import HttpRequest
from ninja import Router

from core.auth.api_key import DeviceAPIKeyAuth
from device.controllers.crash_controller import (
    get_crash_events,
    process_crash_alert,
    submit_crash_feedback,
)
from device.schemas.crash_schema import (
    CrashAlertRequest,
    CrashAlertResponse,
    CrashEventSchema,
    CrashFeedbackRequest,
    CrashFeedbackResponse,
)

logger = logging.getLogger("device")

crash_router = Router(tags=["crash"], auth=DeviceAPIKeyAuth())


@crash_router.post("/alert", response=CrashAlertResponse)
def crash_alert_endpoint(
    request: HttpRequest,
    payload: CrashAlertRequest,
) -> CrashAlertResponse:
    """Endpoint for mobile app to send threshold-triggered crash alerts.

    This is called when Tier 1 (client-side) detects threshold exceeded.
    Backend performs Tier 2 (AI analysis) and responds with confirmation.

    URL: /api/v1/device/crash/alert
    """
    logger.info(
        "[IN] POST /api/v1/device/crash/alert - Crash alert endpoint called (device_id=%s, timestamp=%s)",
        payload.device_id,
        payload.timestamp,
    )
    try:
        response = process_crash_alert(request, payload)
        logger.info(
            "[OK] POST /api/v1/device/crash/alert - Successfully processed (device_id=%s, is_crash=%s)",
            payload.device_id,
            response.is_crash,
        )
        return response
    except Exception as e:
        logger.error(
            "[ERROR] POST /api/v1/device/crash/alert - Error processing crash alert (device_id=%s)",
            payload.device_id,
            exc_info=True,
        )
        raise


@crash_router.get("/events", response=list[CrashEventSchema])
def crash_events_endpoint(
    request: HttpRequest,
    device_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[CrashEventSchema]:
    """Get crash events for a device or user.

    URL: /api/v1/device/crash/events
    """
    logger.info(
        "[IN] GET /api/v1/device/crash/events - Crash events endpoint called (device_id=%s, limit=%s, offset=%s)",
        device_id,
        limit,
        offset,
    )
    try:
        response = get_crash_events(request, device_id, limit, offset)
        logger.info(
            "[OK] GET /api/v1/device/crash/events - Successfully retrieved %s events",
            len(response),
        )
        return response
    except Exception as e:
        logger.error(
            "[ERROR] GET /api/v1/device/crash/events - Error retrieving crash events",
            exc_info=True,
        )
        raise


@crash_router.post("/events/{event_id}/feedback", response=CrashFeedbackResponse)
def crash_feedback_endpoint(
    request: HttpRequest,
    event_id: int,
    payload: CrashFeedbackRequest,
) -> CrashFeedbackResponse:
    """Submit user feedback for a crash event.

    URL: /api/v1/device/crash/events/{event_id}/feedback
    """
    logger.info(
        "[IN] POST /api/v1/device/crash/events/%s/feedback - Crash feedback endpoint called (feedback=%s)",
        event_id,
        payload.user_feedback,
    )
    try:
        response = submit_crash_feedback(request, event_id, payload)
        logger.info(
            "[OK] POST /api/v1/device/crash/events/%s/feedback - Successfully submitted feedback",
            event_id,
        )
        return response
    except Exception as e:
        logger.error(
            "[ERROR] POST /api/v1/device/crash/events/%s/feedback - Error submitting feedback",
            event_id,
            exc_info=True,
        )
        raise

