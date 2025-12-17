"""Mobile app router (uses JWT authentication)."""

from core.auth.jwt import JwtAuth
from django.http import HttpRequest
from ninja import Router

from device.controllers.fcm_controller import register_fcm_token, send_test_notification
from device.schemas.fcm_schema import FCMTokenRequest, FCMTokenResponse, TestNotificationResponse

mobile_router = Router(tags=["mobile"], auth=JwtAuth())


@mobile_router.post("/fcm/token", response=FCMTokenResponse)
def register_fcm_token_endpoint(
    request: HttpRequest,
    payload: FCMTokenRequest,
) -> FCMTokenResponse:
    """Endpoint for mobile app to register FCM push notification tokens.

    Requires JWT authentication (user must be logged in).

    URL: /api/v1/device/mobile/fcm/token
    """
    return register_fcm_token(request, payload)


@mobile_router.post("/fcm/test", response=TestNotificationResponse)
def send_test_notification_endpoint(request: HttpRequest) -> TestNotificationResponse:
    """Endpoint to send a test push notification to the authenticated user's device.

    Requires JWT authentication (user must be logged in).

    URL: /api/v1/device/mobile/fcm/test
    """
    return send_test_notification(request)
