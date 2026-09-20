"""Shopee Affiliate Python Client Library."""

from shopee_affiliate.async_client import AsyncShopeeAffiliateClient
from shopee_affiliate.auth import build_authorization_header, generate_signature
from shopee_affiliate.client import ShopeeAffiliateClient
from shopee_affiliate.errors import (
    ShopeeAPIError,
    ShopeeAuthError,
    ShopeeError,
    ShopeeHTTPError,
    ShopeePermissionError,
    ShopeeRateLimitError,
)
from shopee_affiliate.models import (
    ConversionReport,
    ConversionReportItem,
    ConversionReportOrder,
    PageInfo,
    ProductOffer,
    ShopOffer,
    ShortLinkResult,
)

__version__ = "0.1.0"
__all__ = [
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
