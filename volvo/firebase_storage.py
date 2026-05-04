"""Upload catalog media to Firebase Storage using the Admin SDK."""

from __future__ import annotations

import mimetypes
import uuid
from urllib.parse import quote

from django.core.files.uploadedfile import UploadedFile


def upload_catalog_file(file, storage_relative_path: str) -> str:
    """
    Store a file under ``storage_relative_path`` and return an HTTPS URL the app can load
    (Firebase download URL with token metadata, same pattern as client SDK uploads).
    """
    from firebase_admin import storage

    bucket = storage.bucket()

    blob = bucket.blob(storage_relative_path)
    content_type = None
    if isinstance(file, UploadedFile):
        content_type = getattr(file, "content_type", None) or mimetypes.guess_type(
            getattr(file, "name", "") or ""
        )[0]
    if not content_type:
        content_type = mimetypes.guess_type(storage_relative_path)[0] or "application/octet-stream"

    if hasattr(file, "seek"):
        try:
            file.seek(0)
        except (OSError, AttributeError, ValueError):
            pass
    blob.upload_from_file(file, content_type=content_type)

    token = str(uuid.uuid4())
    new_meta = dict(blob.metadata or {})
    new_meta["firebaseStorageDownloadTokens"] = token
    blob.metadata = new_meta
    blob.patch()

    encoded = quote(storage_relative_path, safe="")
    return (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/"
        f"{encoded}?alt=media&token={token}"
    )
