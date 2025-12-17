"""FCM service for push notifications."""

import logging
from typing import Any

try:
    import firebase_admin
    from firebase_admin import credentials, messaging
except ImportError:
    firebase_admin = None  # type: ignore[assignment]
    credentials = None  # type: ignore[assignment]
    messaging = None  # type: ignore[assignment]

from sentry.settings.config import settings as app_settings

from device.models import CrashEvent, DeviceToken

logger = logging.getLogger(__name__)


class FCMService:
    """Firebase Cloud Messaging service for push notifications."""

    def __init__(self) -> None:
        """Initialize FCM service."""
        if firebase_admin is None:
            logger.warning("firebase-admin package not installed")
            return

        if not firebase_admin._apps:  # noqa: SLF001
            # Initialize Firebase Admin SDK
            cred_path = app_settings.fcm_credentials_path
            if cred_path:
                try:
                    cred = credentials.Certificate(cred_path)  # type: ignore[union-attr]
                    firebase_admin.initialize_app(cred)
                except (ValueError, OSError, TypeError):
                    logger.exception("Failed to initialize Firebase with credentials")
            else:
                logger.warning("FCM credentials path not configured")

    def send_crash_notification(
        self,
        device_id: str,
        crash_event: CrashEvent,
        ai_analysis: dict[str, Any],
    ) -> bool:
        """Send crash notification to user's mobile device.

        Args:
            device_id: Device identifier
            crash_event: CrashEvent model instance
            ai_analysis: AI analysis results from Gemini

        Returns:
            True if notification sent successfully, False otherwise

        """
        if messaging is None:
            logger.error("firebase-admin.messaging not available")
            return False

        try:
            # Get FCM token for device
            fcm_token = self._get_fcm_token(device_id)
            if not fcm_token:
                logger.warning("No FCM token found for device %s", device_id)
                return False

            # Build notification message
            severity = ai_analysis.get("severity", "unknown").upper()
            reasoning = ai_analysis.get("reasoning", "Crash detected")[:100]

            message = messaging.Message(
                notification=messaging.Notification(
                    title="🚨 Crash Detected",
                    body=f"Severity: {severity} | {reasoning}",
                ),
                data={
                    "type": "crash_detected",
                    "crash_event_id": str(crash_event.id),  # type: ignore[attr-defined]
                    "severity": ai_analysis.get("severity", "low"),
                    "confidence": str(ai_analysis.get("confidence", 0.0)),
                    "crash_type": ai_analysis.get("crash_type", "unknown"),
                    "timestamp": crash_event.crash_timestamp.isoformat(),  # type: ignore[attr-defined]
                },
                token=fcm_token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        channel_id="crash_alerts",
                        sound="default",
                        priority="max",
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound="default",
                            badge=1,
                            content_available=True,
                        ),
                    ),
                ),
            )

            # Send notification
            response = messaging.send(message)  # type: ignore[union-attr]
            logger.info("FCM notification sent: %s", response)

            # Update crash event
            crash_event.alert_sent = True  # type: ignore[attr-defined]
            crash_event.save(update_fields=["alert_sent"])
        except Exception:
            logger.exception("Error sending FCM notification")
            return False
        else:
            return True

    def _get_fcm_token(self, device_id: str) -> str | None:
        """Get FCM token for device.

        Args:
            device_id: Device identifier

        Returns:
            FCM token string or None if not found

        """
        try:
            device_token = DeviceToken.objects.filter(  # type: ignore[attr-defined]
                device_id=device_id,
                is_active=True,
            ).first()
        except Exception:
            logger.exception("Error retrieving FCM token")
            return None
        else:
            if device_token:
                return device_token.fcm_token  # type: ignore[attr-defined]
            return None
