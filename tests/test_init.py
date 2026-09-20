"""Tests for package exports and initialization in __init__.py."""

import importlib
import pytest
import shopee_affiliate


EXPECTED_EXPORTS = [
    "ShopeeAffiliateClient",
    "AsyncShopeeAffiliateClient",
    "generate_signature",
    "build_authorization_header",
    "ShopeeError",
    "ShopeeHTTPError",
    "ShopeeAuthError",
    "ShopeeRateLimitError",
    "ShopeePermissionError",
    "ShopeeAPIError",
    "PageInfo",
    "ShortLinkResult",
    "ProductOffer",
    "ShopOffer",
    "ConversionReportItem",
    "ConversionReportOrder",
    "ConversionReport",
]


def test_package_version():
    assert hasattr(shopee_affiliate, "__version__")
    assert shopee_affiliate.__version__ == "0.1.0"


def test_package_all_attribute():
    assert hasattr(shopee_affiliate, "__all__")
    assert isinstance(shopee_affiliate.__all__, list)
    assert set(shopee_affiliate.__all__) == set(EXPECTED_EXPORTS)
    assert len(shopee_affiliate.__all__) == len(EXPECTED_EXPORTS)


def test_all_exports_importable():
    for name in EXPECTED_EXPORTS:
        assert hasattr(shopee_affiliate, name), f"shopee_affiliate is missing export {name}"
        obj = getattr(shopee_affiliate, name)
        assert obj is not None


def test_direct_imports():
    from shopee_affiliate import (
        AsyncShopeeAffiliateClient,
        ConversionReport,
        ConversionReportItem,
        ConversionReportOrder,
        PageInfo,
        ProductOffer,
        ShopOffer,
        ShopeeAPIError,
        ShopeeAffiliateClient,
        ShopeeAuthError,
        ShopeeError,
        ShopeeHTTPError,
        ShopeePermissionError,
        ShopeeRateLimitError,
        ShortLinkResult,
        build_authorization_header,
        generate_signature,
    )

    assert ShopeeAffiliateClient is not None
    assert AsyncShopeeAffiliateClient is not None
    assert callable(generate_signature)
    assert callable(build_authorization_header)
    assert issubclass(ShopeeHTTPError, ShopeeError)
    assert issubclass(ShopeeAuthError, ShopeeError)
    assert issubclass(ShopeeRateLimitError, ShopeeError)
    assert issubclass(ShopeePermissionError, ShopeeError)
    assert issubclass(ShopeeAPIError, ShopeeError)
