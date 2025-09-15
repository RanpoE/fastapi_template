import os
from uuid import uuid4
from typing import Optional


def _require_cloudinary():
    try:
        import cloudinary  # type: ignore
        import cloudinary.uploader  # type: ignore

        return cloudinary
    except Exception as e:
        raise RuntimeError(
            "cloudinary package is required. Install with: pip install cloudinary"
        ) from e


def _configure_cloudinary(cloudinary_module):
    # Prefer CLOUDINARY_URL; otherwise use individual vars
    url = os.environ.get("CLOUDINARY_URL")
    cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME")
    api_key = os.environ.get("CLOUDINARY_API_KEY")
    api_secret = os.environ.get("CLOUDINARY_API_SECRET")

    if url:
        cloudinary_module.config(cloudinary_url=url)
        return
    if cloud_name and api_key and api_secret:
        cloudinary_module.config(
            cloud_name=cloud_name, api_key=api_key, api_secret=api_secret
        )
        return
    raise RuntimeError(
        "Cloudinary credentials missing. "
        "Set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET."
    )


def upload_image_bytes(
    data: bytes,
    original_filename: Optional[str] = None,
    folder: Optional[str] = "recipes",
) -> str:
    """Uploads image bytes to Cloudinary, returns secure URL."""
    cloudinary = _require_cloudinary()
    _configure_cloudinary(cloudinary)

    public_id = uuid4().hex

    try:
        result = cloudinary.uploader.upload(
            data,
            resource_type="image",
            folder=folder,
            public_id=public_id,
            filename=original_filename or f"{public_id}.jpg",
            unique_filename=True,
            overwrite=False,
        )
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {e}") from e

    url = result.get("secure_url") or result.get("url")
    if not url:
        raise RuntimeError("Cloudinary did not return a URL")
    return url
