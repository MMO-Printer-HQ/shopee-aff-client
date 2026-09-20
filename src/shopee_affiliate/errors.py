"""Custom exceptions and error mapping for Shopee Affiliate API."""

from typing import Any


class ShopeeError(Exception):
    """Base exception for all Shopee Affiliate library errors."""

    def __init__(
        self,
        message: str,
        error_code: int | None = None,
        raw_response: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.raw_response = raw_response or {}

    def __str__(self) -> str:
        if self.error_code is not None:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ShopeeHTTPError(ShopeeError):
    """Raised when an HTTP error or connection failure occurs."""

    def __init__(self, message: str, status_code: int | None = None, content: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.content = content


class ShopeeAuthError(ShopeeError):
    """Raised when authentication fails (10020)."""


class ShopeeRateLimitError(ShopeeError):
    """Raised when rate limit is exceeded (10030)."""


class ShopeePermissionError(ShopeeError):
    """Raised when account lacks permission or is frozen (10031, 10033, 10034, 10035)."""


class ShopeeAPIError(ShopeeError):
    """Raised for business/GraphQL API errors."""


def map_shopee_error(
    code: int,
    message: str,
    raw_response: dict[str, Any] | None = None,
) -> ShopeeError:
    """Map Shopee numeric error code to specialized exception."""
    if code == 10020:
        return ShopeeAuthError(message, error_code=code, raw_response=raw_response)
    if code == 10030:
        return ShopeeRateLimitError(message, error_code=code, raw_response=raw_response)
    if code in (10031, 10032, 10033, 10034, 10035):
        return ShopeePermissionError(message, error_code=code, raw_response=raw_response)
    return ShopeeAPIError(message, error_code=code, raw_response=raw_response)
