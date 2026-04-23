"""Send FCM notifications using the same Firebase Admin app as auth."""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def send_fcm_to_user(
    user,
    title: str,
    body: str,
    data: Optional[dict[str, Any]] = None,
) -> bool:
    """
    Send a notification to the user's device(s). Requires user.notification_token
    to be set (from the mobile app).
    """
    token = (getattr(user, "notification_token", None) or "").strip()
    if not token:
        return False
    try:
        from firebase_admin import messaging

        payload: dict = {
            "notification": messaging.Notification(title=title, body=body),
            "token": token,
        }
        if data:
            payload["data"] = {k: str(v) for k, v in data.items() if v is not None}
        msg = messaging.Message(**payload)
        messaging.send(msg)
        return True
    except Exception as e:
        logger.exception("FCM send failed (user_id=%s): %s", getattr(user, "pk", None), e)
        return False
