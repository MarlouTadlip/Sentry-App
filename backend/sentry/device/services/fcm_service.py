"""Push notification service using Expo Push Notification API."""

import logging
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore[assignment]

from sentry.settings.config import settings as app_settings

from device.models import CrashEvent, DeviceToken

logger = logging.getLogger(__name__)


class FCMService:
    """Push notification service using Expo Push Notification API.

    This service sends push notifications to mobile devices using Expo's
    Push Notification Service. The app sends Expo Push Tokens which are
    compatible with this service.
    """

    def __init__(self) -> None:
        """Initialize push notification service."""
        if httpx is None:
            logger.warning("httpx package not installed. Install it with: pip install httpx")

    def send_crash_notification(
        self,
        device_id: str,
        crash_event: CrashEvent,
        ai_analysis: dict[str, Any],
    ) -> bool:
        """Send crash notification to user's mobile device using Expo Push Notification API.

        Args:
            device_id: Device identifier
            crash_event: CrashEvent model instance
            ai_analysis: AI analysis results from Gemini

        Returns:
            True if notification sent successfully, False otherwise

        """
        if httpx is None:
            logger.error("httpx package not available. Install it with: pip install httpx")
            return False

        try:
            # Get Expo Push Token for device
            expo_token = self._get_expo_push_token(device_id)
            if not expo_token:
                logger.warning("No Expo push token found for device %s", device_id)
                return False

            # Build notification message for Expo Push API
            severity = ai_analysis.get("severity", "unknown").upper()
            reasoning = ai_analysis.get("reasoning", "Crash detected")[:100]

            # Get GPS location if available
            gps_location = None
            map_link = None
            if crash_event.crash_latitude and crash_event.crash_longitude:  # type: ignore[attr-defined]
                gps_location = {
                    "latitude": crash_event.crash_latitude,  # type: ignore[attr-defined]
                    "longitude": crash_event.crash_longitude,  # type: ignore[attr-defined]
                    "altitude": crash_event.crash_altitude,  # type: ignore[attr-defined]
                }
                map_link = f"https://www.google.com/maps?q={crash_event.crash_latitude},{crash_event.crash_longitude}"  # type: ignore[attr-defined]

            # Prepare notification payload for Expo Push API
            message = {
                "to": expo_token,
                "sound": "default",
                "title": "🚨 Crash Detected",
                "body": f"Severity: {severity} | {reasoning}",
                "data": {
                    "type": "crash_detected",
                    "crash_event_id": str(crash_event.id),  # type: ignore[attr-defined]
                    "severity": ai_analysis.get("severity", "low"),
                    "confidence": str(ai_analysis.get("confidence", 0.0)),
                    "crash_type": ai_analysis.get("crash_type", "unknown"),
                    "timestamp": crash_event.crash_timestamp.isoformat(),  # type: ignore[attr-defined]
                    "gps_location": gps_location,
                    "map_link": map_link,
                },
                "priority": "high",  # High priority for crash notifications
                "channelId": "crash_alerts",  # Android notification channel
            }

            # Send notification via Expo Push API
            return self._send_expo_notification(device_id, message, crash_event)

        except httpx.HTTPError:
            logger.exception("HTTP error sending Expo push notification")
        except Exception:
            logger.exception("Error sending Expo push notification")

        return False

    def _send_expo_notification(
        self,
        device_id: str,
        message: dict[str, Any],
        crash_event: CrashEvent,
    ) -> bool:
        """Send notification via Expo API and handle response.

        Args:
            device_id: Device identifier for logging
            message: Notification message payload
            crash_event: CrashEvent to update on success

        Returns:
            True if notification sent successfully, False otherwise

        """
        if httpx is None:
            return False

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                app_settings.expo_push_api_url,
                json=message,
                headers={
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            result = response.json()

            # Expo API returns a list of results, one per notification
            # Each result has a "status" field: "ok" or "error"
            # Sometimes the response is wrapped in a "data" key: {"data": {"status": "ok"}}
            status = None
            if isinstance(result, list) and len(result) > 0:
                status = result[0].get("status")
                if status != "ok":
                    error_message = result[0].get("message", "Unknown error")
                    logger.error("Failed to send Expo push notification: %s", error_message)
                    return False
            elif isinstance(result, dict):
                # Check for nested data structure first: {"data": {"status": "ok"}}
                if "data" in result and isinstance(result.get("data"), dict):
                    status = result["data"].get("status")
                else:
                    status = result.get("status")

                if status != "ok":
                    logger.error("Failed to send Expo push notification: %s", result)
                    return False
            else:
                logger.error("Unexpected response format from Expo API: %s", result)
                return False

            if status == "ok":
                logger.info("Expo push notification sent successfully for device %s", device_id)
                crash_event.alert_sent = True  # type: ignore[attr-defined]
                crash_event.save(update_fields=["alert_sent"])
                return True

            return False

    def send_test_notification(
        self,
        device_id: str,
        title: str = "🧪 Test Notification",
        body: str = "This is a test notification from the backend",
    ) -> bool:
        """Send a test push notification to a device.

        Args:
            device_id: Device identifier
            title: Notification title (default: test notification)
            body: Notification body (default: test message)

        Returns:
            True if notification sent successfully, False otherwise

        """
        if httpx is None:
            logger.error("httpx package not available. Install it with: pip install httpx")
            return False

        try:
            # Get Expo Push Token for device
            expo_token = self._get_expo_push_token(device_id)
            if not expo_token:
                logger.warning("No Expo push token found for device %s", device_id)
                return False

            # Prepare test notification payload
            message = {
                "to": expo_token,
                "sound": "default",
                "title": title,
                "body": body,
                "data": {
                    "type": "test_notification",
                    "timestamp": str(int(__import__("time").time())),
                },
                "priority": "default",
            }

            # Send notification via Expo Push API (without crash_event)
            return self._send_expo_notification_without_crash_event(device_id, message)

        except Exception:
            logger.exception("Error sending test notification")
            return False

    def _send_expo_notification_without_crash_event(
        self,
        device_id: str,
        message: dict[str, Any],
    ) -> bool:
        """Send notification via Expo API without updating crash_event.

        Args:
            device_id: Device identifier for logging
            message: Notification message payload

        Returns:
            True if notification sent successfully, False otherwise

        """
        if httpx is None:
            return False

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                app_settings.expo_push_api_url,
                json=message,
                headers={
                    "Accept": "application/json",
                    "Accept-encoding": "gzip, deflate",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            result = response.json()

            # Expo API returns a list of results, one per notification
            # Each result has a "status" field: "ok" or "error"
            # Sometimes the response is wrapped in a "data" key: {"data": {"status": "ok"}}
            status = None
            if isinstance(result, list) and len(result) > 0:
                status = result[0].get("status")
                if status != "ok":
                    error_message = result[0].get("message", "Unknown error")
                    logger.error("Failed to send Expo push notification: %s", error_message)
                    return False
            elif isinstance(result, dict):
                # Check for nested data structure first: {"data": {"status": "ok"}}
                if "data" in result and isinstance(result.get("data"), dict):
                    status = result["data"].get("status")
                else:
                    status = result.get("status")

                if status != "ok":
                    logger.error("Failed to send Expo push notification: %s", result)
                    return False
            else:
                logger.error("Unexpected response format from Expo API: %s", result)
                return False

            if status == "ok":
                logger.info("Expo push notification sent successfully for device %s", device_id)
                return True

            return False

    def _get_expo_push_token(self, device_id: str) -> str | None:
        """Get Expo Push Token for device.

        Args:
            device_id: Device identifier

        Returns:
            Expo Push Token string or None if not found

        """
        try:
            device_token = DeviceToken.objects.filter(  # type: ignore[attr-defined]
                device_id=device_id,
                is_active=True,
            ).first()
        except Exception:
            logger.exception("Error retrieving Expo push token")
            return None

        if device_token:
            # The fcm_token field actually stores Expo Push Tokens
            return device_token.fcm_token  # type: ignore[attr-defined]
        return None
