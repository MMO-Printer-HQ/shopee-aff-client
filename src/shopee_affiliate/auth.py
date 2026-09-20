"""Authentication and request signing for Shopee Affiliate API."""

import hashlib
import time


def generate_signature(app_id: str, secret: str, payload: str, timestamp: int) -> str:
    """Generate SHA-256 signature for Shopee Affiliate API request.

    Signature formula: SHA256(app_id + timestamp + payload + secret)
    """
    signature_base = f"{app_id}{timestamp}{payload}{secret}"
    return hashlib.sha256(signature_base.encode("utf-8")).hexdigest()


def build_authorization_header(
    app_id: str,
    secret: str,
    payload: str,
    timestamp: int | None = None,
) -> tuple[str, int]:
    """Construct Authorization header value and return (header_value, timestamp_used)."""
    if timestamp is None:
        timestamp = int(time.time())

    signature = generate_signature(
        app_id=app_id,
        secret=secret,
        payload=payload,
        timestamp=timestamp,
    )
    header = f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}"
    return header, timestamp
