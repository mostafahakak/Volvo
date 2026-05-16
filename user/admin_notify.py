"""Notify dashboard staff via FCM (tokens stored on User.notification_token)."""
from __future__ import annotations

import logging
from typing import Any, Optional

from user.fcm_push import send_fcm_to_user
from user.models import User

logger = logging.getLogger(__name__)


def notify_all_staff_fcm(
    title: str,
    body: str,
    *,
    data: Optional[dict[str, Any]] = None,
) -> int:
    """
    Push to every active staff user who saved an FCM token (mobile dashboard).

    Returns the number of sends reported successful by Firebase.
    """
    qs = (
        User.objects.filter(is_staff=True, is_active=True)
        .exclude(notification_token__isnull=True)
        .exclude(notification_token="")
    )
    sent = 0
    for admin_user in qs.iterator():
        try:
            if send_fcm_to_user(admin_user, title, body, data=data):
                sent += 1
        except Exception:
            logger.exception(
                "staff FCM notify failed staff_id=%s", getattr(admin_user, "pk", None)
            )
    return sent
