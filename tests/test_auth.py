"""Tests for authentication and signature generation."""

import hashlib
from shopee_affiliate.auth import generate_signature, build_authorization_header


def test_generate_signature():
    app_id = "123456"
    secret = "secret_xyz"
    payload = '{"query":"mutation{generateShortLink(input:{originUrl:\\"https://shopee.vn\\"}){shortLink}}"}'
    timestamp = 1577836800

    expected_base = f"{app_id}{timestamp}{payload}{secret}"
    expected_sig = hashlib.sha256(expected_base.encode("utf-8")).hexdigest()

    sig = generate_signature(app_id=app_id, secret=secret, payload=payload, timestamp=timestamp)
    assert sig == expected_sig


def test_build_authorization_header():
    app_id = "123456"
    secret = "secret_xyz"
    payload = '{"query":"{}"}'
    timestamp = 1700000000

    header, ts = build_authorization_header(app_id=app_id, secret=secret, payload=payload, timestamp=timestamp)
    assert ts == timestamp
    sig = generate_signature(app_id, secret, payload, timestamp)
    assert header == f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={sig}"


def test_build_authorization_header_default_timestamp():
    app_id = "123456"
    secret = "secret_xyz"
    payload = '{"query":"{}"}'

    header, ts = build_authorization_header(app_id=app_id, secret=secret, payload=payload)
    assert ts > 0
    expected_sig = generate_signature(app_id, secret, payload, ts)
    assert header == f"SHA256 Credential={app_id}, Timestamp={ts}, Signature={expected_sig}"
