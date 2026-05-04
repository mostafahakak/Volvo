"""Upload catalog media to Firebase Storage using the Admin SDK."""

from __future__ import annotations

import mimetypes
import uuid
from urllib.parse import quote

from django.core.files.uploadedfile import UploadedFile


class FirebaseUploadError(Exception):
    """Raised when a file cannot be stored in Firebase (wrong bucket, permissions, empty file, etc.)."""


def upload_catalog_file(file, storage_relative_path: str) -> str:
    """
    Store a file under ``storage_relative_path`` and return an HTTPS URL the app can load
    (Firebase download URL with token metadata, same pattern as client SDK uploads).
    """
    from firebase_admin import storage

    try:
        bucket = storage.bucket()
    except ValueError as e:
        raise FirebaseUploadError(
            "Firebase Storage is not configured. Set storageBucket on initialize_app "
            "(see FIREBASE_STORAGE_BUCKET / project_id in settings)."
        ) from e

    blob = bucket.blob(storage_relative_path)
    content_type = None
    if isinstance(file, UploadedFile):
        if getattr(file, "size", None) == 0:
            raise FirebaseUploadError("Image file is empty.")
        content_type = getattr(file, "content_type", None) or mimetypes.guess_type(
            getattr(file, "name", "") or ""
        )[0]
    if not content_type:
        content_type = mimetypes.guess_type(storage_relative_path)[0] or "application/octet-stream"

    if hasattr(file, "read"):
        try:
            file.seek(0)
        except (OSError, AttributeError, ValueError):
            pass
        raw = file.read()
    else:
        raw = file
    if not raw:
        raise FirebaseUploadError("Image file is empty.")

    token = str(uuid.uuid4())
    blob.metadata = dict(blob.metadata or {})
    blob.metadata["firebaseStorageDownloadTokens"] = token

    try:
        blob.upload_from_string(raw, content_type=content_type)
    except Exception as e:
        msg = str(e)
        if "404" in msg or "Not Found" in msg:
            raise FirebaseUploadError(
                "Firebase Storage bucket not found. Set FIREBASE_STORAGE_BUCKET in Render to the exact "
                'value in Firebase Console → Storage / google-services.json (e.g. volvoegyptapp.firebasestorage.app).'
            ) from e
        if "403" in msg or "Permission" in msg.lower():
            raise FirebaseUploadError(
                "Firebase Storage permission denied. Ensure the service account has Storage Object Admin (or "
                "Firebase Admin) on this project."
            ) from e
        raise FirebaseUploadError(f"Firebase upload failed: {msg}") from e

    encoded = quote(storage_relative_path, safe="")
    return (
        f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/"
        f"{encoded}?alt=media&token={token}"
    )
