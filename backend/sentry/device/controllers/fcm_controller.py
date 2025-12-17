"""FCM token registration controller."""

import logging

from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError

from device.models import DeviceToken
from device.schemas.fcm_schema import FCMTokenRequest, FCMTokenResponse, TestNotificationResponse
from device.services.fcm_service import FCMService

logger = logging.getLogger("device")


def register_fcm_token(
    request: HttpRequest,
    data: FCMTokenRequest,
) -> FCMTokenResponse:
    """Register or update FCM token for a device.

    Args:
        request: HTTP request object (should have authenticated user)
        data: FCM token registration data

    Returns:
        FCMTokenResponse with success status

    Raises:
        HttpError: If registration fails

    """
    try:
        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None  # type: ignore[attr-defined]

        with transaction.atomic():  # type: ignore[call-overload]
            # Try to find existing token for this device_id and fcm_token combination
            device_token, created = DeviceToken.objects.get_or_create(  # type: ignore[attr-defined]
                device_id=data.device_id,
                fcm_token=data.fcm_token,
                defaults={
                    "user": user,
                    "platform": data.platform,
                    "is_active": True,
                },
            )

            if not created:
                # Update existing token
                device_token.user = user  # type: ignore[attr-defined]
                device_token.platform = data.platform  # type: ignore[attr-defined]
                device_token.is_active = True  # type: ignore[attr-defined]
                device_token.save(update_fields=["user", "platform", "is_active", "updated_at"])

            logger.info(
                "FCM token %s for device %s (platform: %s, user: %s)",
                "registered" if created else "updated",
                data.device_id,
                data.platform,
                user.id if user else "anonymous",  # type: ignore[attr-defined]
            )

            return FCMTokenResponse(
                success=True,
                message=f"FCM token {'registered' if created else 'updated'} successfully",
            )

    except Exception:
        logger.exception("Error registering FCM token")
        raise HttpError(status_code=500, message="Failed to register FCM token") from None


def send_test_notification(request: HttpRequest) -> TestNotificationResponse:
    """Send a test push notification to the authenticated user's device.

    Args:
        request: HTTP request object (should have authenticated user)

    Returns:
        TestNotificationResponse with success status

    Raises:
        HttpError: If sending fails

    """
    try:
        user = request.user if hasattr(request, "user") and request.user.is_authenticated else None  # type: ignore[attr-defined]

        if not user:
            raise HttpError(status_code=401, message="Authentication required")

        # Get the device token for the current user
        # We'll use the most recent active token
        device_token = DeviceToken.objects.filter(  # type: ignore[attr-defined]
            user=user,
            is_active=True,
        ).order_by("-updated_at").first()

        if not device_token:
            return TestNotificationResponse(
                success=False,
                message="No active push token found for your device. Please ensure notifications are enabled in the app.",
            )

        # Send test notification
        fcm_service = FCMService()
        success = fcm_service.send_test_notification(
            device_id=device_token.device_id,  # type: ignore[attr-defined]
            title="🧪 Test Push Notification",
            body="This is a test notification sent from the backend to verify FCM is working correctly!",
        )

        if success:
            logger.info("Test notification sent successfully to user %s", user.id)  # type: ignore[attr-defined]
            return TestNotificationResponse(
                success=True,
                message="Test notification sent successfully",
            )

        return TestNotificationResponse(
            success=False,
            message="Failed to send test notification. Check server logs for details.",
        )

    except HttpError:
        raise
    except Exception:
        logger.exception("Error sending test notification")
        raise HttpError(status_code=500, message="Failed to send test notification") from None
