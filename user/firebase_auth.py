"""Verify Firebase ID tokens (phone auth). Firebase app is initialized in settings when credentials exist."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def verify_firebase_id_token(id_token: str) -> Optional[Dict[str, Any]]:
    """
    Returns decoded token dict (includes 'phone_number', 'uid') or None if invalid.
    """
    if not id_token:
        return None
    try:
        from firebase_admin import auth

        return auth.verify_id_token(id_token)
    except Exception as e:
        # Common causes: wrong service account project vs mobile app, or Admin SDK not initialized on server.
        logger.warning("verify_id_token failed (%s): %s", type(e).__name__, e)
        return None
