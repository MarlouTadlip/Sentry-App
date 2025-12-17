"""Crash router."""

from django.http import HttpRequest
from ninja import Router

from core.auth.api_key import DeviceAPIKeyAuth
from device.controllers.crash_controller import process_crash_alert
from device.schemas.crash_schema import CrashAlertRequest, CrashAlertResponse

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
    return process_crash_alert(request, payload)

