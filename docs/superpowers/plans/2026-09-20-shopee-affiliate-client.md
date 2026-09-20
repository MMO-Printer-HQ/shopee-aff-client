# Shopee Affiliate Python Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a robust, lightweight Python client library for the Shopee Affiliate Open API (GraphQL) supporting both synchronous and asynchronous operations using `httpx`, type-safe dataclasses, plain SHA-256 request signing, and cursor-based pagination.

**Architecture:** A modular library separating pure SHA-256 authentication signing (`auth.py`), strongly typed dataclasses (`models.py`), error definitions (`errors.py`), GraphQL templates (`queries.py`), and base transport logic (`base.py`) powering dual synchronous (`ShopeeAffiliateClient`) and asynchronous (`AsyncShopeeAffiliateClient`) clients.

**Tech Stack:** Python >= 3.11, `uv` package manager, `hatchling` build backend, `httpx >= 0.24.0`, `pytest`, `pytest-asyncio`.

## Global Constraints
- Target Runtime: Python >= 3.11.
- Package Manager: `uv` with standard `pyproject.toml`.
- Sole Runtime Dependency: `httpx >= 0.24.0`.
- Authentication signature format: `SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}` where `Signature = hashlib.sha256(f"{app_id}{timestamp}{payload}{secret}".encode("utf-8")).hexdigest()`.

---

### Task 1: Project Setup & Package Scaffolding with `uv`

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `src/shopee_affiliate/__init__.py`

**Interfaces:**
- Consumes: None
- Produces: Project environment managed by `uv` with `httpx`, `pytest`, `pytest-asyncio` installed.

- [ ] **Step 1: Write `.gitignore`**
```gitignore
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv/
env/
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/
```

- [ ] **Step 2: Write `pyproject.toml`**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shopee-affiliate"
version = "0.1.0"
description = "Modern Python client library for Shopee Affiliate Open API"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
authors = [
    { name = "Shopee Affiliate Client Contributors" }
]
dependencies = [
    "httpx>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/shopee_affiliate"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 3: Create stub `src/shopee_affiliate/__init__.py`**
```python
"""Shopee Affiliate Python Client."""

__version__ = "0.1.0"
```

- [ ] **Step 4: Initialize virtual environment and sync dependencies using `uv`**
Run: `uv venv && uv pip install -e ".[dev]"`
Expected: Virtual environment created at `.venv` and packages installed.

- [ ] **Step 5: Verify environment**
Run: `uv run pytest`
Expected: 0 tests collected (no errors).

- [ ] **Step 6: Commit**
```bash
git add pyproject.toml .gitignore src/shopee_affiliate/__init__.py
git commit -m "chore: scaffold project structure with uv and pyproject.toml"
```

---

### Task 2: Authentication & Signature Generation (`auth.py`)

**Files:**
- Create: `src/shopee_affiliate/auth.py`
- Create: `tests/test_auth.py`

**Interfaces:**
- Consumes: Standard `hashlib`, `time`
- Produces:
  - `generate_signature(app_id: str, secret: str, payload: str, timestamp: int) -> str`
  - `build_authorization_header(app_id: str, secret: str, payload: str, timestamp: int | None = None) -> tuple[str, int]`

- [ ] **Step 1: Write the failing test for signature and header**
```python
# tests/test_auth.py
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
    assert f"Timestamp={ts}" in header
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_auth.py`
Expected: FAIL (ModuleNotFoundError or ImportError: cannot import name 'generate_signature')

- [ ] **Step 3: Write `src/shopee_affiliate/auth.py` implementation**
```python
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
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_auth.py`
Expected: PASS (3 tests passed)

- [ ] **Step 5: Commit**
```bash
git add src/shopee_affiliate/auth.py tests/test_auth.py
git commit -m "feat: implement shopee sha256 authentication and authorization header builder"
```

---

### Task 3: Exceptions & Data Models (`errors.py` & `models.py`)

**Files:**
- Create: `src/shopee_affiliate/errors.py`
- Create: `src/shopee_affiliate/models.py`
- Create: `tests/test_models.py`

**Interfaces:**
- Consumes: Standard `dataclasses`, `typing`
- Produces:
  - Exceptions: `ShopeeError`, `ShopeeHTTPError`, `ShopeeAuthError`, `ShopeeRateLimitError`, `ShopeePermissionError`, `ShopeeAPIError`
  - Models: `PageInfo`, `ShortLinkResult`, `ProductOffer`, `ShopOffer`, `ConversionReportItem`, `ConversionReportOrder`, `ConversionReport`

- [ ] **Step 1: Write the failing tests for models and errors**
```python
# tests/test_models.py
from shopee_affiliate.models import (
    PageInfo,
    ShortLinkResult,
    ProductOffer,
    ShopOffer,
    ConversionReportItem,
    ConversionReportOrder,
    ConversionReport,
)
from shopee_affiliate.errors import (
    ShopeeError,
    ShopeeAuthError,
    ShopeeRateLimitError,
    ShopeePermissionError,
    ShopeeAPIError,
    map_shopee_error,
)

def test_short_link_model():
    data = {"shortLink": "https://shope.ee/xyz123"}
    res = ShortLinkResult.from_dict(data)
    assert res.short_link == "https://shope.ee/xyz123"
    assert res.to_dict()["shortLink"] == "https://shope.ee/xyz123"

def test_product_offer_model():
    data = {
        "itemId": 12345,
        "productName": "Awesome Product",
        "productLink": "https://shopee.vn/p-12345",
        "offerLink": "https://shope.ee/p12345",
        "commissionRate": "0.15",
        "sales": 50,
        "shopId": 999,
        "shopName": "Shop A",
    }
    offer = ProductOffer.from_dict(data)
    assert offer.item_id == 12345
    assert offer.product_name == "Awesome Product"
    assert offer.commission_rate == "0.15"
    assert offer.sales == 50
    assert offer.shop_id == 999

def test_conversion_report_model():
    data = {
        "conversionId": 987654321,
        "purchaseTime": 1700000000,
        "clickTime": 1699999000,
        "totalCommission": "50000",
        "sellerCommission": "30000",
        "shopeeCommissionCapped": "20000",
        "orders": [
            {
                "orderId": "ORD123",
                "orderStatus": "COMPLETED",
                "shopType": "SHOPEE_MALL",
                "items": [
                    {
                        "itemId": 111,
                        "itemName": "Shirt",
                        "itemPrice": "100000",
                        "qty": 2,
                        "actualAmount": "200000",
                        "itemTotalCommission": "20000",
                        "itemSellerCommission": "10000",
                        "itemShopeeCommissionCapped": "10000",
                        "displayItemStatus": "COMPLETED",
                    }
                ],
            }
        ],
    }
    report = ConversionReport.from_dict(data)
    assert report.conversion_id == 987654321
    assert len(report.orders) == 1
    assert report.orders[0].order_id == "ORD123"
    assert len(report.orders[0].items) == 1
    assert report.orders[0].items[0].item_id == 111

def test_error_mapping():
    err_auth = map_shopee_error(10020, "Invalid signature")
    assert isinstance(err_auth, ShopeeAuthError)

    err_limit = map_shopee_error(10030, "Rate limit")
    assert isinstance(err_limit, ShopeeRateLimitError)

    err_perm = map_shopee_error(10031, "Access denied")
    assert isinstance(err_perm, ShopeePermissionError)

    err_api = map_shopee_error(11000, "General business error")
    assert isinstance(err_api, ShopeeAPIError)
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_models.py`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement `src/shopee_affiliate/errors.py`**
```python
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
```

- [ ] **Step 4: Implement `src/shopee_affiliate/models.py`**
```python
"""Data models for Shopee Affiliate API responses."""

from dataclasses import dataclass, field
from typing import Any, Self


@dataclass(slots=True)
class PageInfo:
    page: int | None = None
    limit: int | None = None
    has_next_page: bool | None = None
    scroll_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            page=data.get("page"),
            limit=data.get("limit"),
            has_next_page=data.get("hasNextPage"),
            scroll_id=data.get("scrollId"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "page": self.page,
            "limit": self.limit,
            "hasNextPage": self.has_next_page,
            "scrollId": self.scroll_id,
        }


@dataclass(slots=True)
class ShortLinkResult:
    short_link: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(short_link=data.get("shortLink", ""))

    def to_dict(self) -> dict[str, Any]:
        return {"shortLink": self.short_link}


@dataclass(slots=True)
class ProductOffer:
    item_id: int
    product_name: str
    product_link: str
    offer_link: str
    image_url: str = ""
    commission_rate: str = "0"
    seller_commission_rate: str = "0"
    shopee_commission_rate: str = "0"
    commission: str = "0"
    price_min: str = "0"
    price_max: str = "0"
    sales: int = 0
    rating_star: str = "0"
    price_discount_rate: int = 0
    shop_id: int | None = None
    shop_name: str = ""
    shop_type: list[int] = field(default_factory=list)
    product_cat_ids: list[int] = field(default_factory=list)
    period_start_time: int | None = None
    period_end_time: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            item_id=int(data.get("itemId", 0)),
            product_name=data.get("productName", ""),
            product_link=data.get("productLink", ""),
            offer_link=data.get("offerLink", ""),
            image_url=data.get("imageUrl", ""),
            commission_rate=str(data.get("commissionRate", "0")),
            seller_commission_rate=str(data.get("sellerCommissionRate", "0")),
            shopee_commission_rate=str(data.get("shopeeCommissionRate", "0")),
            commission=str(data.get("commission", "0")),
            price_min=str(data.get("priceMin", "0")),
            price_max=str(data.get("priceMax", "0")),
            sales=int(data.get("sales", 0)),
            rating_star=str(data.get("ratingStar", "0")),
            price_discount_rate=int(data.get("priceDiscountRate", 0)),
            shop_id=int(data["shopId"]) if data.get("shopId") is not None else None,
            shop_name=data.get("shopName", ""),
            shop_type=data.get("shopType") or [],
            product_cat_ids=data.get("productCatIds") or [],
            period_start_time=data.get("periodStartTime"),
            period_end_time=data.get("periodEndTime"),
            raw=data,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "itemId": self.item_id,
            "productName": self.product_name,
            "productLink": self.product_link,
            "offerLink": self.offer_link,
            "imageUrl": self.image_url,
            "commissionRate": self.commission_rate,
            "sellerCommissionRate": self.seller_commission_rate,
            "shopeeCommissionRate": self.shopee_commission_rate,
            "commission": self.commission,
            "priceMin": self.price_min,
            "priceMax": self.price_max,
            "sales": self.sales,
            "ratingStar": self.rating_star,
            "priceDiscountRate": self.price_discount_rate,
            "shopId": self.shop_id,
            "shopName": self.shop_name,
            "shopType": self.shop_type,
            "productCatIds": self.product_cat_ids,
            "periodStartTime": self.period_start_time,
            "periodEndTime": self.period_end_time,
        }


@dataclass(slots=True)
class ShopOffer:
    shop_id: int
    shop_name: str
    offer_link: str
    original_link: str
    commission_rate: str = "0"
    seller_comm_cove_ratio: str = "0"
    rating_star: str = "0"
    image_url: str = ""
    shop_type: list[int] = field(default_factory=list)
    period_start_time: int | None = None
    period_end_time: int | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            shop_id=int(data.get("shopId", 0)),
            shop_name=data.get("shopName", ""),
            offer_link=data.get("offerLink", ""),
            original_link=data.get("originalLink", ""),
            commission_rate=str(data.get("commissionRate", "0")),
            seller_comm_cove_ratio=str(data.get("sellerCommCoveRatio", "0")),
            rating_star=str(data.get("ratingStar", "0")),
            image_url=data.get("imageUrl", ""),
            shop_type=data.get("shopType") or [],
            period_start_time=data.get("periodStartTime"),
            period_end_time=data.get("periodEndTime"),
            raw=data,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "shopId": self.shop_id,
            "shopName": self.shop_name,
            "offerLink": self.offer_link,
            "originalLink": self.original_link,
            "commissionRate": self.commission_rate,
            "sellerCommCoveRatio": self.seller_comm_cove_ratio,
            "ratingStar": self.rating_star,
            "imageUrl": self.image_url,
            "shopType": self.shop_type,
            "periodStartTime": self.period_start_time,
            "periodEndTime": self.period_end_time,
        }


@dataclass(slots=True)
class ConversionReportItem:
    item_id: int
    item_name: str
    item_price: str
    qty: int
    actual_amount: str
    item_total_commission: str
    item_seller_commission: str
    item_shopee_commission_capped: str
    display_item_status: str
    order_id: str = ""
    shop_id: int | None = None
    shop_name: str = ""
    complete_time: int | None = None
    image_url: str = ""
    fraud_status: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            item_id=int(data.get("itemId", 0)),
            item_name=data.get("itemName", ""),
            item_price=str(data.get("itemPrice", "0")),
            qty=int(data.get("qty", 0)),
            actual_amount=str(data.get("actualAmount", "0")),
            item_total_commission=str(data.get("itemTotalCommission", "0")),
            item_seller_commission=str(data.get("itemSellerCommission", "0")),
            item_shopee_commission_capped=str(data.get("itemShopeeCommissionCapped", "0")),
            display_item_status=data.get("displayItemStatus", ""),
            order_id=str(data.get("orderId", "")),
            shop_id=int(data["shopId"]) if data.get("shopId") is not None else None,
            shop_name=data.get("shopName", ""),
            complete_time=data.get("completeTime"),
            image_url=data.get("imageUrl", ""),
            fraud_status=data.get("fraudStatus", ""),
            raw=data,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "itemId": self.item_id,
            "itemName": self.item_name,
            "itemPrice": self.item_price,
            "qty": self.qty,
            "actualAmount": self.actual_amount,
            "itemTotalCommission": self.item_total_commission,
            "itemSellerCommission": self.item_seller_commission,
            "itemShopeeCommissionCapped": self.item_shopee_commission_capped,
            "displayItemStatus": self.display_item_status,
            "orderId": self.order_id,
            "shopId": self.shop_id,
            "shopName": self.shop_name,
            "completeTime": self.complete_time,
            "imageUrl": self.image_url,
            "fraudStatus": self.fraud_status,
        }


@dataclass(slots=True)
class ConversionReportOrder:
    order_id: str
    order_status: str
    shop_type: str
    items: list[ConversionReportItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        raw_items = data.get("items") or []
        return cls(
            order_id=str(data.get("orderId", "")),
            order_status=data.get("orderStatus", ""),
            shop_type=data.get("shopType", ""),
            items=[ConversionReportItem.from_dict(item) for item in raw_items],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "orderId": self.order_id,
            "orderStatus": self.order_status,
            "shopType": self.shop_type,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(slots=True)
class ConversionReport:
    conversion_id: int
    purchase_time: int
    click_time: int
    total_commission: str
    seller_commission: str
    shopee_commission_capped: str
    net_commission: str = ""
    buyer_type: str = ""
    utm_content: str = ""
    device: str = ""
    orders: list[ConversionReportOrder] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        raw_orders = data.get("orders") or []
        return cls(
            conversion_id=int(data.get("conversionId", 0)),
            purchase_time=int(data.get("purchaseTime", 0)),
            click_time=int(data.get("clickTime", 0)),
            total_commission=str(data.get("totalCommission", "0")),
            seller_commission=str(data.get("sellerCommission", "0")),
            shopee_commission_capped=str(data.get("shopeeCommissionCapped", "0")),
            net_commission=str(data.get("netCommission", "")),
            buyer_type=data.get("buyerType", ""),
            utm_content=data.get("utmContent", ""),
            device=data.get("device", ""),
            orders=[ConversionReportOrder.from_dict(order) for order in raw_orders],
            raw=data,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversionId": self.conversion_id,
            "purchaseTime": self.purchase_time,
            "clickTime": self.click_time,
            "totalCommission": self.total_commission,
            "sellerCommission": self.seller_commission,
            "shopeeCommissionCapped": self.shopee_commission_capped,
            "netCommission": self.net_commission,
            "buyerType": self.buyer_type,
            "utmContent": self.utm_content,
            "device": self.device,
            "orders": [order.to_dict() for order in self.orders],
        }
```

- [ ] **Step 5: Run tests to verify they pass**
Run: `uv run pytest tests/test_models.py`
Expected: PASS (4 tests passed)

- [ ] **Step 6: Commit**
```bash
git add src/shopee_affiliate/errors.py src/shopee_affiliate/models.py tests/test_models.py
git commit -m "feat: implement data models and error hierarchy"
```

---

### Task 4: GraphQL Queries & Base Transport Logic (`queries.py` & `base.py`)

**Files:**
- Create: `src/shopee_affiliate/queries.py`
- Create: `src/shopee_affiliate/base.py`
- Create: `tests/test_base.py`

**Interfaces:**
- Consumes: `auth.py`, `errors.py`
- Produces:
  - `GENERATE_SHORT_LINK_MUTATION`, `PRODUCT_OFFER_QUERY`, `SHOP_OFFER_QUERY`, `CONVERSION_REPORT_QUERY`, `VALIDATED_REPORT_QUERY`
  - `serialize_graphql_payload(query: str, variables: dict | None = None) -> str`
  - `process_graphql_response(status_code: int, response_json: dict) -> dict`

- [ ] **Step 1: Write test for payload serialization and response processing**
```python
# tests/test_base.py
import pytest
from shopee_affiliate.base import serialize_graphql_payload, process_graphql_response
from shopee_affiliate.errors import ShopeeAuthError, ShopeeAPIError, ShopeeHTTPError

def test_serialize_graphql_payload():
    query = "query { test }"
    payload = serialize_graphql_payload(query, {"foo": "bar"})
    assert '"query":"query { test }"' in payload
    assert '"variables":{"foo":"bar"}' in payload

def test_process_graphql_response_success():
    data = {"data": {"generateShortLink": {"shortLink": "https://shope.ee/test"}}}
    result = process_graphql_response(200, data)
    assert result == data["data"]

def test_process_graphql_response_errors():
    data = {
        "errors": [{"message": "Invalid credential", "code": 10020}],
    }
    with pytest.raises(ShopeeAuthError) as exc_info:
        process_graphql_response(200, data)
    assert exc_info.value.error_code == 10020

def test_process_graphql_response_http_error():
    with pytest.raises(ShopeeHTTPError):
        process_graphql_response(500, {})
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_base.py`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement `src/shopee_affiliate/queries.py`**
```python
"""Standard GraphQL query and mutation templates for Shopee Affiliate API."""

GENERATE_SHORT_LINK_MUTATION = """
mutation generateShortLink($input: ShortLinkInput!) {
  generateShortLink(input: $input) {
    shortLink
  }
}
""".strip()

PRODUCT_OFFER_QUERY = """
query productOfferV2(
  $keyword: String
  $itemId: Int64
  $shopId: Int64
  $productCatId: Int32
  $listType: Int
  $sortType: Int
  $page: Int
  $limit: Int
  $isAMSOffer: Boolean
  $isKeySeller: Boolean
) {
  productOfferV2(
    keyword: $keyword
    itemId: $itemId
    shopId: $shopId
    productCatId: $productCatId
    listType: $listType
    sortType: $sortType
    page: $page
    limit: $limit
    isAMSOffer: $isAMSOffer
    isKeySeller: $isKeySeller
  ) {
    nodes {
      itemId
      productName
      productLink
      offerLink
      imageUrl
      commissionRate
      sellerCommissionRate
      shopeeCommissionRate
      commission
      priceMin
      priceMax
      sales
      ratingStar
      priceDiscountRate
      shopId
      shopName
      shopType
      productCatIds
      periodStartTime
      periodEndTime
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
""".strip()

SHOP_OFFER_QUERY = """
query shopOfferV2(
  $shopId: Int64
  $keyword: String
  $shopType: [Int]
  $isKeySeller: Boolean
  $sortType: Int
  $page: Int
  $limit: Int
) {
  shopOfferV2(
    shopId: $shopId
    keyword: $keyword
    shopType: $shopType
    isKeySeller: $isKeySeller
    sortType: $sortType
    page: $page
    limit: $limit
  ) {
    nodes {
      shopId
      shopName
      offerLink
      originalLink
      commissionRate
      sellerCommCoveRatio
      ratingStar
      imageUrl
      shopType
      periodStartTime
      periodEndTime
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
""".strip()

CONVERSION_REPORT_QUERY = """
query conversionReport(
  $purchaseTimeStart: Int
  $purchaseTimeEnd: Int
  $completeTimeStart: Int
  $completeTimeEnd: Int
  $shopName: String
  $shopId: Int64
  $orderId: String
  $orderStatus: String
  $limit: Int
  $scrollId: String
) {
  conversionReport(
    purchaseTimeStart: $purchaseTimeStart
    purchaseTimeEnd: $purchaseTimeEnd
    completeTimeStart: $completeTimeStart
    completeTimeEnd: $completeTimeEnd
    shopName: $shopName
    shopId: $shopId
    orderId: $orderId
    orderStatus: $orderStatus
    limit: $limit
    scrollId: $scrollId
  ) {
    nodes {
      conversionId
      purchaseTime
      clickTime
      totalCommission
      sellerCommission
      shopeeCommissionCapped
      netCommission
      buyerType
      utmContent
      device
      orders {
        orderId
        orderStatus
        shopType
        items {
          itemId
          itemName
          itemPrice
          qty
          actualAmount
          itemTotalCommission
          itemSellerCommission
          itemShopeeCommissionCapped
          displayItemStatus
          orderId
          shopId
          shopName
          completeTime
          imageUrl
          fraudStatus
        }
      }
    }
    pageInfo {
      limit
      hasNextPage
      scrollId
    }
  }
}
""".strip()

VALIDATED_REPORT_QUERY = """
query validatedReport(
  $validationId: Int64!
  $limit: Int
  $scrollId: String
) {
  validatedReport(
    validationId: $validationId
    limit: $limit
    scrollId: $scrollId
  ) {
    nodes {
      conversionId
      purchaseTime
      clickTime
      totalCommission
      sellerCommission
      shopeeCommissionCapped
      netCommission
      orders {
        orderId
        orderStatus
        shopType
        items {
          itemId
          itemName
          itemPrice
          qty
          actualAmount
          itemTotalCommission
          itemSellerCommission
          itemShopeeCommissionCapped
          displayItemStatus
          orderId
          shopId
          shopName
          completeTime
        }
      }
    }
    pageInfo {
      limit
      hasNextPage
      scrollId
    }
  }
}
""".strip()
```

- [ ] **Step 4: Implement `src/shopee_affiliate/base.py`**
```python
"""Base transport and GraphQL payload processing utilities."""

import json
from typing import Any
from shopee_affiliate.errors import ShopeeHTTPError, map_shopee_error, ShopeeAPIError

DEFAULT_BASE_URL = "https://open-api.affiliate.shopee.vn/graphql"


def serialize_graphql_payload(query: str, variables: dict[str, Any] | None = None) -> str:
    """Serialize query and variables to compact JSON string without extra whitespace."""
    data: dict[str, Any] = {"query": query}
    if variables:
        data["variables"] = variables
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def process_graphql_response(status_code: int, response_json: dict[str, Any]) -> dict[str, Any]:
    """Inspect HTTP response and GraphQL payload for errors and return data payload."""
    if status_code != 200:
        raise ShopeeHTTPError(
            f"Shopee API returned HTTP {status_code}",
            status_code=status_code,
            content=json.dumps(response_json),
        )

    # Check for GraphQL errors
    errors = response_json.get("errors")
    if errors and isinstance(errors, list) and len(errors) > 0:
        first_error = errors[0]
        code = first_error.get("code")
        message = first_error.get("message") or str(first_error)
        if isinstance(code, int):
            raise map_shopee_error(code, message, raw_response=response_json)
        raise ShopeeAPIError(message, raw_response=response_json)

    # Check top-level error code if present
    code = response_json.get("code")
    if code is not None and code != 0:
        message = response_json.get("message", "Unknown error")
        raise map_shopee_error(int(code), message, raw_response=response_json)

    data = response_json.get("data")
    if data is None:
        raise ShopeeAPIError("Missing 'data' field in response", raw_response=response_json)

    return data
```

- [ ] **Step 5: Run tests to verify they pass**
Run: `uv run pytest tests/test_base.py`
Expected: PASS (4 tests passed)

- [ ] **Step 6: Commit**
```bash
git add src/shopee_affiliate/queries.py src/shopee_affiliate/base.py tests/test_base.py
git commit -m "feat: add graphql queries, payload serialization, and response validator"
```

---

### Task 5: Synchronous Client (`client.py`)

**Files:**
- Create: `src/shopee_affiliate/client.py`
- Create: `tests/test_client_sync.py`

**Interfaces:**
- Consumes: `auth.py`, `models.py`, `errors.py`, `queries.py`, `base.py`, `httpx.Client`
- Produces: `ShopeeAffiliateClient` with methods:
  - `generate_short_link(origin_url, sub_ids)`
  - `get_product_offers(keyword, itemId, ...)`
  - `get_shop_offers(keyword, shopId, ...)`
  - `get_conversion_report(purchase_time_start, ...)`
  - `iter_conversion_reports(...)`
  - `execute(query, variables)`

- [ ] **Step 1: Write test for synchronous client using `httpx.MockTransport`**
```python
# tests/test_client_sync.py
import json
import httpx
from shopee_affiliate.client import ShopeeAffiliateClient
from shopee_affiliate.models import ProductOffer, ConversionReport

def mock_transport_handler(request: httpx.Request) -> httpx.Response:
    assert request.headers.get("Authorization", "").startswith("SHA256 Credential=")
    body = json.loads(request.content.decode("utf-8"))
    query = body.get("query", "")

    if "generateShortLink" in query:
        return httpx.Response(
            200,
            json={"data": {"generateShortLink": {"shortLink": "https://shope.ee/mocked"}}},
        )
    if "productOfferV2" in query:
        return httpx.Response(
            200,
            json={
                "data": {
                    "productOfferV2": {
                        "nodes": [
                            {
                                "itemId": 12345,
                                "productName": "Mock Phone",
                                "productLink": "https://shopee.vn/mock",
                                "offerLink": "https://shope.ee/mock",
                                "commissionRate": "0.10",
                            }
                        ],
                        "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
                    }
                }
            },
        )
    if "conversionReport" in query:
        return httpx.Response(
            200,
            json={
                "data": {
                    "conversionReport": {
                        "nodes": [
                            {
                                "conversionId": 999,
                                "purchaseTime": 1700000000,
                                "clickTime": 1699990000,
                                "totalCommission": "1000",
                                "sellerCommission": "500",
                                "shopeeCommissionCapped": "500",
                                "orders": [],
                            }
                        ],
                        "pageInfo": {"limit": 10, "hasNextPage": False, "scrollId": "scroll_123"},
                    }
                }
            },
        )

    return httpx.Response(400, json={"message": "Not Found"})

def test_sync_generate_short_link():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    with ShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        link = client.generate_short_link("https://shopee.vn/item-1", sub_ids=["sub1"])
        assert link == "https://shope.ee/mocked"

def test_sync_get_product_offers():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    with ShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        offers, page_info = client.get_product_offers(keyword="Phone")
        assert len(offers) == 1
        assert isinstance(offers[0], ProductOffer)
        assert offers[0].item_id == 12345
        assert page_info.has_next_page is False

def test_sync_get_conversion_report():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    with ShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        reports, page_info = client.get_conversion_report(limit=10)
        assert len(reports) == 1
        assert isinstance(reports[0], ConversionReport)
        assert reports[0].conversion_id == 999
        assert page_info.scroll_id == "scroll_123"
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_client_sync.py`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement `src/shopee_affiliate/client.py`**
```python
"""Synchronous Shopee Affiliate API Client."""

from typing import Any, Iterator, Self
import httpx

from shopee_affiliate.auth import build_authorization_header
from shopee_affiliate.base import (
    DEFAULT_BASE_URL,
    process_graphql_response,
    serialize_graphql_payload,
)
from shopee_affiliate.models import (
    ConversionReport,
    PageInfo,
    ProductOffer,
    ShopOffer,
    ShortLinkResult,
)
from shopee_affiliate.queries import (
    CONVERSION_REPORT_QUERY,
    GENERATE_SHORT_LINK_MUTATION,
    PRODUCT_OFFER_QUERY,
    SHOP_OFFER_QUERY,
    VALIDATED_REPORT_QUERY,
)


class ShopeeAffiliateClient:
    """Client for synchronous interaction with Shopee Affiliate Open API."""

    def __init__(
        self,
        app_id: str,
        secret: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.app_id = app_id
        self.secret = secret
        self.base_url = base_url
        self._http = httpx.Client(
            timeout=timeout,
            transport=transport,
            headers={"Content-Type": "application/json"},
        )

    def close(self) -> None:
        """Close the underlying HTTP client session."""
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a raw GraphQL query or mutation with signature authorization."""
        payload = serialize_graphql_payload(query, variables)
        auth_header, _ = build_authorization_header(self.app_id, self.secret, payload)

        response = self._http.post(
            self.base_url,
            content=payload,
            headers={"Authorization": auth_header},
        )
        return process_graphql_response(response.status_code, response.json())

    def generate_short_link(
        self,
        origin_url: str,
        sub_ids: list[str] | None = None,
    ) -> str:
        """Convert a Shopee origin link into an affiliate short link."""
        input_data: dict[str, Any] = {"originUrl": origin_url}
        if sub_ids is not None:
            input_data["subIds"] = sub_ids

        data = self.execute(
            GENERATE_SHORT_LINK_MUTATION,
            variables={"input": input_data},
        )
        short_link_data = data.get("generateShortLink", {})
        result = ShortLinkResult.from_dict(short_link_data)
        return result.short_link

    def get_product_offers(
        self,
        keyword: str | None = None,
        item_id: int | None = None,
        shop_id: int | None = None,
        product_cat_id: int | None = None,
        list_type: int | None = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10,
        is_ams_offer: bool | None = None,
        is_key_seller: bool | None = None,
    ) -> tuple[list[ProductOffer], PageInfo]:
        """Query product offers."""
        variables: dict[str, Any] = {
            "sortType": sort_type,
            "page": page,
            "limit": limit,
        }
        if keyword is not None:
            variables["keyword"] = keyword
        if item_id is not None:
            variables["itemId"] = item_id
        if shop_id is not None:
            variables["shopId"] = shop_id
        if product_cat_id is not None:
            variables["productCatId"] = product_cat_id
        if list_type is not None:
            variables["listType"] = list_type
        if is_ams_offer is not None:
            variables["isAMSOffer"] = is_ams_offer
        if is_key_seller is not None:
            variables["isKeySeller"] = is_key_seller

        data = self.execute(PRODUCT_OFFER_QUERY, variables=variables)
        offer_connection = data.get("productOfferV2", {})
        nodes = offer_connection.get("nodes") or []
        page_info_data = offer_connection.get("pageInfo") or {}

        offers = [ProductOffer.from_dict(node) for node in nodes]
        page_info = PageInfo.from_dict(page_info_data)
        return offers, page_info

    def get_shop_offers(
        self,
        keyword: str | None = None,
        shop_id: int | None = None,
        shop_type: list[int] | None = None,
        is_key_seller: bool | None = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[ShopOffer], PageInfo]:
        """Query shop offers."""
        variables: dict[str, Any] = {
            "sortType": sort_type,
            "page": page,
            "limit": limit,
        }
        if keyword is not None:
            variables["keyword"] = keyword
        if shop_id is not None:
            variables["shopId"] = shop_id
        if shop_type is not None:
            variables["shopType"] = shop_type
        if is_key_seller is not None:
            variables["isKeySeller"] = is_key_seller

        data = self.execute(SHOP_OFFER_QUERY, variables=variables)
        offer_connection = data.get("shopOfferV2", {})
        nodes = offer_connection.get("nodes") or []
        page_info_data = offer_connection.get("pageInfo") or {}

        offers = [ShopOffer.from_dict(node) for node in nodes]
        page_info = PageInfo.from_dict(page_info_data)
        return offers, page_info

    def get_conversion_report(
        self,
        purchase_time_start: int | None = None,
        purchase_time_end: int | None = None,
        complete_time_start: int | None = None,
        complete_time_end: int | None = None,
        shop_name: str | None = None,
        shop_id: int | None = None,
        order_id: str | None = None,
        order_status: str | None = None,
        limit: int = 50,
        scroll_id: str | None = None,
    ) -> tuple[list[ConversionReport], PageInfo]:
        """Query conversion reports."""
        variables: dict[str, Any] = {"limit": limit}
        if purchase_time_start is not None:
            variables["purchaseTimeStart"] = purchase_time_start
        if purchase_time_end is not None:
            variables["purchaseTimeEnd"] = purchase_time_end
        if complete_time_start is not None:
            variables["completeTimeStart"] = complete_time_start
        if complete_time_end is not None:
            variables["completeTimeEnd"] = complete_time_end
        if shop_name is not None:
            variables["shopName"] = shop_name
        if shop_id is not None:
            variables["shopId"] = shop_id
        if order_id is not None:
            variables["orderId"] = order_id
        if order_status is not None:
            variables["orderStatus"] = order_status
        if scroll_id is not None:
            variables["scrollId"] = scroll_id

        data = self.execute(CONVERSION_REPORT_QUERY, variables=variables)
        report_connection = data.get("conversionReport", {})
        nodes = report_connection.get("nodes") or []
        page_info_data = report_connection.get("pageInfo") or {}

        reports = [ConversionReport.from_dict(node) for node in nodes]
        page_info = PageInfo.from_dict(page_info_data)
        return reports, page_info

    def iter_conversion_reports(
        self,
        purchase_time_start: int | None = None,
        purchase_time_end: int | None = None,
        limit_per_page: int = 50,
        max_results: int | None = None,
    ) -> Iterator[ConversionReport]:
        """Automatically page through conversion reports using scrollId."""
        current_scroll_id: str | None = None
        count = 0

        while True:
            reports, page_info = self.get_conversion_report(
                purchase_time_start=purchase_time_start,
                purchase_time_end=purchase_time_end,
                limit=limit_per_page,
                scroll_id=current_scroll_id,
            )
            if not reports:
                break

            for report in reports:
                yield report
                count += 1
                if max_results is not None and count >= max_results:
                    return

            if not page_info.scroll_id:
                break
            current_scroll_id = page_info.scroll_id
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_client_sync.py`
Expected: PASS (3 tests passed)

- [ ] **Step 5: Commit**
```bash
git add src/shopee_affiliate/client.py tests/test_client_sync.py
git commit -m "feat: implement synchronous ShopeeAffiliateClient"
```

---

### Task 6: Asynchronous Client (`async_client.py`)

**Files:**
- Create: `src/shopee_affiliate/async_client.py`
- Create: `tests/test_client_async.py`

**Interfaces:**
- Consumes: `auth.py`, `models.py`, `errors.py`, `queries.py`, `base.py`, `httpx.AsyncClient`
- Produces: `AsyncShopeeAffiliateClient` with async counterparts of methods.

- [ ] **Step 1: Write test for asynchronous client using `httpx.MockTransport`**
```python
# tests/test_client_async.py
import json
import pytest
import httpx
from shopee_affiliate.async_client import AsyncShopeeAffiliateClient
from shopee_affiliate.models import ProductOffer, ConversionReport

def mock_transport_handler(request: httpx.Request) -> httpx.Response:
    assert request.headers.get("Authorization", "").startswith("SHA256 Credential=")
    body = json.loads(request.content.decode("utf-8"))
    query = body.get("query", "")

    if "generateShortLink" in query:
        return httpx.Response(
            200,
            json={"data": {"generateShortLink": {"shortLink": "https://shope.ee/async_mocked"}}},
        )
    if "productOfferV2" in query:
        return httpx.Response(
            200,
            json={
                "data": {
                    "productOfferV2": {
                        "nodes": [
                            {
                                "itemId": 54321,
                                "productName": "Async Item",
                                "productLink": "https://shopee.vn/async",
                                "offerLink": "https://shope.ee/async",
                                "commissionRate": "0.20",
                            }
                        ],
                        "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
                    }
                }
            },
        )
    if "conversionReport" in query:
        return httpx.Response(
            200,
            json={
                "data": {
                    "conversionReport": {
                        "nodes": [
                            {
                                "conversionId": 888,
                                "purchaseTime": 1700000000,
                                "clickTime": 1699990000,
                                "totalCommission": "2000",
                                "sellerCommission": "1000",
                                "shopeeCommissionCapped": "1000",
                                "orders": [],
                            }
                        ],
                        "pageInfo": {"limit": 10, "hasNextPage": False, "scrollId": "scroll_async_123"},
                    }
                }
            },
        )

    return httpx.Response(400, json={"message": "Not Found"})

@pytest.mark.asyncio
async def test_async_generate_short_link():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        link = await client.generate_short_link("https://shopee.vn/item-1")
        assert link == "https://shope.ee/async_mocked"

@pytest.mark.asyncio
async def test_async_get_product_offers():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        offers, page_info = await client.get_product_offers(keyword="Async Item")
        assert len(offers) == 1
        assert isinstance(offers[0], ProductOffer)
        assert offers[0].item_id == 54321

@pytest.mark.asyncio
async def test_async_get_conversion_report():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        reports, page_info = await client.get_conversion_report(limit=10)
        assert len(reports) == 1
        assert isinstance(reports[0], ConversionReport)
        assert reports[0].conversion_id == 888
```

- [ ] **Step 2: Run test to verify it fails**
Run: `uv run pytest tests/test_client_async.py`
Expected: FAIL (ImportError)

- [ ] **Step 3: Implement `src/shopee_affiliate/async_client.py`**
```python
"""Asynchronous Shopee Affiliate API Client."""

from typing import Any, AsyncIterator, Self
import httpx

from shopee_affiliate.auth import build_authorization_header
from shopee_affiliate.base import (
    DEFAULT_BASE_URL,
    process_graphql_response,
    serialize_graphql_payload,
)
from shopee_affiliate.models import (
    ConversionReport,
    PageInfo,
    ProductOffer,
    ShopOffer,
    ShortLinkResult,
)
from shopee_affiliate.queries import (
    CONVERSION_REPORT_QUERY,
    GENERATE_SHORT_LINK_MUTATION,
    PRODUCT_OFFER_QUERY,
    SHOP_OFFER_QUERY,
)


class AsyncShopeeAffiliateClient:
    """Client for asynchronous interaction with Shopee Affiliate Open API."""

    def __init__(
        self,
        app_id: str,
        secret: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.app_id = app_id
        self.secret = secret
        self.base_url = base_url
        self._http = httpx.AsyncClient(
            timeout=timeout,
            transport=transport,
            headers={"Content-Type": "application/json"},
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP client session."""
        await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    async def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a raw GraphQL query or mutation with signature authorization."""
        payload = serialize_graphql_payload(query, variables)
        auth_header, _ = build_authorization_header(self.app_id, self.secret, payload)

        response = await self._http.post(
            self.base_url,
            content=payload,
            headers={"Authorization": auth_header},
        )
        return process_graphql_response(response.status_code, response.json())

    async def generate_short_link(
        self,
        origin_url: str,
        sub_ids: list[str] | None = None,
    ) -> str:
        """Convert a Shopee origin link into an affiliate short link asynchronously."""
        input_data: dict[str, Any] = {"originUrl": origin_url}
        if sub_ids is not None:
            input_data["subIds"] = sub_ids

        data = await self.execute(
            GENERATE_SHORT_LINK_MUTATION,
            variables={"input": input_data},
        )
        short_link_data = data.get("generateShortLink", {})
        result = ShortLinkResult.from_dict(short_link_data)
        return result.short_link

    async def get_product_offers(
        self,
        keyword: str | None = None,
        item_id: int | None = None,
        shop_id: int | None = None,
        product_cat_id: int | None = None,
        list_type: int | None = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10,
        is_ams_offer: bool | None = None,
        is_key_seller: bool | None = None,
    ) -> tuple[list[ProductOffer], PageInfo]:
        """Query product offers asynchronously."""
        variables: dict[str, Any] = {
            "sortType": sort_type,
            "page": page,
            "limit": limit,
        }
        if keyword is not None:
            variables["keyword"] = keyword
        if item_id is not None:
            variables["itemId"] = item_id
        if shop_id is not None:
            variables["shopId"] = shop_id
        if product_cat_id is not None:
            variables["productCatId"] = product_cat_id
        if list_type is not None:
            variables["listType"] = list_type
        if is_ams_offer is not None:
            variables["isAMSOffer"] = is_ams_offer
        if is_key_seller is not None:
            variables["isKeySeller"] = is_key_seller

        data = await self.execute(PRODUCT_OFFER_QUERY, variables=variables)
        offer_connection = data.get("productOfferV2", {})
        nodes = offer_connection.get("nodes") or []
        page_info_data = offer_connection.get("pageInfo") or {}

        offers = [ProductOffer.from_dict(node) for node in nodes]
        page_info = PageInfo.from_dict(page_info_data)
        return offers, page_info

    async def get_shop_offers(
        self,
        keyword: str | None = None,
        shop_id: int | None = None,
        shop_type: list[int] | None = None,
        is_key_seller: bool | None = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10,
    ) -> tuple[list[ShopOffer], PageInfo]:
        """Query shop offers asynchronously."""
        variables: dict[str, Any] = {
            "sortType": sort_type,
            "page": page,
            "limit": limit,
        }
        if keyword is not None:
            variables["keyword"] = keyword
        if shop_id is not None:
            variables["shopId"] = shop_id
        if shop_type is not None:
            variables["shopType"] = shop_type
        if is_key_seller is not None:
            variables["isKeySeller"] = is_key_seller

        data = await self.execute(SHOP_OFFER_QUERY, variables=variables)
        offer_connection = data.get("shopOfferV2", {})
        nodes = offer_connection.get("nodes") or []
        page_info_data = offer_connection.get("pageInfo") or {}

        offers = [ShopOffer.from_dict(node) for node in nodes]
        page_info = PageInfo.from_dict(page_info_data)
        return offers, page_info

    async def get_conversion_report(
        self,
        purchase_time_start: int | None = None,
        purchase_time_end: int | None = None,
        complete_time_start: int | None = None,
        complete_time_end: int | None = None,
        shop_name: str | None = None,
        shop_id: int | None = None,
        order_id: str | None = None,
        order_status: str | None = None,
        limit: int = 50,
        scroll_id: str | None = None,
    ) -> tuple[list[ConversionReport], PageInfo]:
        """Query conversion reports asynchronously."""
        variables: dict[str, Any] = {"limit": limit}
        if purchase_time_start is not None:
            variables["purchaseTimeStart"] = purchase_time_start
        if purchase_time_end is not None:
            variables["purchaseTimeEnd"] = purchase_time_end
        if complete_time_start is not None:
            variables["completeTimeStart"] = complete_time_start
        if complete_time_end is not None:
            variables["completeTimeEnd"] = complete_time_end
        if shop_name is not None:
            variables["shopName"] = shop_name
        if shop_id is not None:
            variables["shopId"] = shop_id
        if order_id is not None:
            variables["orderId"] = order_id
        if order_status is not None:
            variables["orderStatus"] = order_status
        if scroll_id is not None:
            variables["scrollId"] = scroll_id

        data = await self.execute(CONVERSION_REPORT_QUERY, variables=variables)
        report_connection = data.get("conversionReport", {})
        nodes = report_connection.get("nodes") or []
        page_info_data = report_connection.get("pageInfo") or {}

        reports = [ConversionReport.from_dict(node) for node in nodes]
        page_info = PageInfo.from_dict(page_info_data)
        return reports, page_info

    async def iter_conversion_reports(
        self,
        purchase_time_start: int | None = None,
        purchase_time_end: int | None = None,
        limit_per_page: int = 50,
        max_results: int | None = None,
    ) -> AsyncIterator[ConversionReport]:
        """Automatically page through conversion reports asynchronously using scrollId."""
        current_scroll_id: str | None = None
        count = 0

        while True:
            reports, page_info = await self.get_conversion_report(
                purchase_time_start=purchase_time_start,
                purchase_time_end=purchase_time_end,
                limit=limit_per_page,
                scroll_id=current_scroll_id,
            )
            if not reports:
                break

            for report in reports:
                yield report
                count += 1
                if max_results is not None and count >= max_results:
                    return

            if not page_info.scroll_id:
                break
            current_scroll_id = page_info.scroll_id
```

- [ ] **Step 4: Run test to verify it passes**
Run: `uv run pytest tests/test_client_async.py`
Expected: PASS (3 tests passed)

- [ ] **Step 5: Commit**
```bash
git add src/shopee_affiliate/async_client.py tests/test_client_async.py
git commit -m "feat: implement asynchronous AsyncShopeeAffiliateClient"
```

---

### Task 7: Package Exports, Documentation & Verification

**Files:**
- Modify: `src/shopee_affiliate/__init__.py`
- Create: `README.md`

**Interfaces:**
- Consumes: All modules
- Produces: Top-level package exports, complete README documentation with usage examples for both sync and async.

- [ ] **Step 1: Update `src/shopee_affiliate/__init__.py` with full public exports**
```python
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
```

- [ ] **Step 2: Create `README.md` with complete installation and quickstart guide**
Document:
- Installation via `pip` and `uv add`
- Synchronous client usage example (generating short link, querying product offers, fetching conversion report)
- Asynchronous client usage example
- Custom GraphQL query execution (`client.execute`)
- Error handling patterns

- [ ] **Step 3: Run entire test suite to ensure full passing**
Run: `uv run pytest -v`
Expected: All tests pass with 100% success.

- [ ] **Step 4: Commit**
```bash
git add src/shopee_affiliate/__init__.py README.md
git commit -m "docs: add comprehensive readme and package exports"
```
