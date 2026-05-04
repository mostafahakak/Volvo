"""Create in-app notification rows and send FCM when a token exists."""
from __future__ import annotations

from typing import Any, Optional

from user.fcm_push import send_fcm_to_user


def notify_user_record(
    user,
    *,
    kind: str,
    title: str,
    body: str,
    booking_id: Optional[int] = None,
    extra_fcm_data: Optional[dict[str, Any]] = None,
) -> None:
    from app.models import Booking
    from user.models import UserNotification

    booking = None
    if booking_id is not None:
        booking = Booking.objects.filter(pk=booking_id).first()

    UserNotification.objects.create(
        user=user,
        kind=kind,
        title=(title or "")[:255],
        body=body or "",
        booking=booking,
    )
    data = {k: str(v) for k, v in (extra_fcm_data or {}).items() if v is not None}
    data.setdefault("type", kind)
    if booking_id is not None:
        data["booking_id"] = str(booking_id)
    send_fcm_to_user(
        user,
        title=title or "Volvo",
        body=body or "",
        data=data or None,
    )
