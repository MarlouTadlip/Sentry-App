"""Crash utilities."""

import logging

from device.models import CrashEvent, DeviceToken
from device.services.fcm_service import FCMService

logger = logging.getLogger("device")


def notify_loved_ones_with_gps(
    device_id: str,
    crash_event: CrashEvent,
) -> None:
    """Send GPS location to all active loved ones for the device owner.

    Args:
        device_id: The device ID
        crash_event: The crash event with GPS location
    """
    from core.models import LovedOne

    # Get device owner (user)
    user = crash_event.user  # type: ignore[attr-defined]
    if not user:
        logger.warning("No user associated with crash event %s", crash_event.id)  # type: ignore[attr-defined]
        return

    # Get all active loved ones (use select_related to avoid N+1 queries)
    loved_ones = LovedOne.objects.filter(  # type: ignore[attr-defined]
        user=user,
        is_active=True,
    ).select_related("loved_one")

    # Get GPS location
    if not (crash_event.crash_latitude and crash_event.crash_longitude):  # type: ignore[attr-defined]
        logger.warning("No GPS location for crash event %s", crash_event.id)  # type: ignore[attr-defined]
        return

    map_link = f"https://www.google.com/maps?q={crash_event.crash_latitude},{crash_event.crash_longitude}"  # type: ignore[attr-defined]

    # Initialize FCM service
    fcm_service = FCMService()

    # Send notification to each loved one
    for loved_one_rel in loved_ones:
        loved_one_user = loved_one_rel.loved_one  # type: ignore[attr-defined]

        # Get loved one's device tokens
        device_tokens = DeviceToken.objects.filter(  # type: ignore[attr-defined]
            user=loved_one_user,
            is_active=True,
        )

        for device_token in device_tokens:
            message = {
                "to": device_token.fcm_token,  # type: ignore[attr-defined]
                "sound": "default",
                "title": f"🚨 Emergency: {user.email} - Crash Detected",
                "body": f"Location: {map_link}",
                "data": {
                    "type": "loved_one_crash_alert",
                    "crash_event_id": str(crash_event.id),  # type: ignore[attr-defined]
                    "user_email": user.email,
                    "gps_location": {
                        "latitude": crash_event.crash_latitude,  # type: ignore[attr-defined]
                        "longitude": crash_event.crash_longitude,  # type: ignore[attr-defined]
                        "altitude": crash_event.crash_altitude,  # type: ignore[attr-defined]
                    },
                    "map_link": map_link,
                },
                "priority": "high",
                "channelId": "crash_alerts",
            }

            # Send notification using FCM service's internal method
            try:
                fcm_service._send_expo_notification_without_crash_event(
                    device_id=device_token.device_id or "unknown",  # type: ignore[attr-defined]
                    message=message,
                )
                logger.info(
                    "Sent crash notification to loved one %s for crash event %s",
                    loved_one_user.email,
                    crash_event.id,  # type: ignore[attr-defined]
                )
            except Exception:
                logger.exception(
                    "Error sending crash notification to loved one %s",
                    loved_one_user.email,
                )

