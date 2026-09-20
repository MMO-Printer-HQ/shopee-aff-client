# Design Specification: Shopee Affiliate Python Client Library

- **Date:** 2026-09-20
- **Status:** Approved
- **Target Runtime:** Python >= 3.11
- **Package Name:** `shopee-affiliate` (import name: `shopee_affiliate`)
- **Primary Dependency:** `httpx >= 0.24.0`

---

## 1. Overview & Purpose

A lightweight, modern Python client library for integrating with the official Shopee Affiliate Open API (GraphQL). The library supports both synchronous and asynchronous operations using `httpx`, provides type-annotated standard dataclasses without heavy third-party parsing dependencies, and handles request signing, authentication, error mapping, and pagination.

---

## 2. Requirements & Scope

### 2.1 Functional Scope
1. **Authentication & Request Signing**:
   - SHA-256 signature generator based on Shopee formula: `SHA256(app_id + timestamp + payload + secret)`.
   - Formatted header: `Authorization: SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}`.
   - Support for custom base GraphQL URLs (defaults to `https://open-api.affiliate.shopee.vn/graphql` with option for `https://open-api.affiliate.shopee.com/graphql`).

2. **Affiliate Link Generation**:
   - Mutation `generateShortLink(input: { originUrl, subIds })`.
   - Returns short affiliate tracking link.

3. **Offers Querying**:
   - `productOfferV2`: Query product offers with filters (keyword, itemId, shopId, productCatId, sortType, page, limit, isAMSOffer, isKeySeller).
   - `shopOfferV2`: Query shop offers with filters (shopId, keyword, shopType, isKeySeller, sortType, page, limit).
   - `brandOffer`: Query brand offers (keyword, sortType, page, limit).

4. **Conversion & Validation Reporting**:
   - `conversionReport`: Query order conversion logs with filters (purchase/complete timestamp ranges, scrollId, limit, etc.).
   - `validatedReport`: Query validated orders by `validationId` and `scrollId`.
   - Automatic cursor pagination helper (`iter_conversion_reports` generator respecting 30s scrollId validity).

5. **Low-level Execution**:
   - `execute(query, variables=None)`: Allows arbitrary GraphQL queries/mutations to be executed directly with automatic signature handling.

### 2.2 Non-Functional Requirements
- **Runtime**: Python 3.11+.
- **Minimal Dependencies**: Only `httpx`. No Pydantic or heavy frameworks; use Python built-in `dataclasses` and `typing`.
- **Dual Client Support**: Native `ShopeeAffiliateClient` (sync) and `AsyncShopeeAffiliateClient` (async).
- **Resource Management**: Context manager protocol support (`with` / `async with`).
- **Comprehensive Error Handling**: Structured exception hierarchy mapping Shopee API error codes.

---

## 3. Architecture & Project Layout

```text
shopee-aff-client/
├── pyproject.toml
├── README.md
├── src/
│   └── shopee_affiliate/
│       ├── __init__.py
│       ├── auth.py
│       ├── base.py
│       ├── client.py
│       ├── async_client.py
│       ├── models.py
│       ├── queries.py
│       └── errors.py
└── tests/
    ├── conftest.py
    ├── test_auth.py
    ├── test_client_sync.py
    ├── test_client_async.py
    └── test_models.py
```

### 3.1 Module Responsibilities

- **`auth.py`**:
  - `generate_signature(app_id: str, secret: str, payload: str, timestamp: int) -> str`
  - `build_authorization_header(app_id: str, secret: str, payload: str, timestamp: int | None = None) -> tuple[str, int]`
- **`base.py`**:
  - Common configuration: `app_id`, `secret`, `base_url`, `timeout`.
  - Payload serialization (ensures compact UTF-8 JSON without unintended spacing).
  - Common response checking (`_check_response(status_code, response_json)`).
- **`client.py`**:
  - `ShopeeAffiliateClient`: Synchronous client wrapping `httpx.Client`.
- **`async_client.py`**:
  - `AsyncShopeeAffiliateClient`: Asynchronous client wrapping `httpx.AsyncClient`.
- **`queries.py`**:
  - Constant GraphQL query strings for `generateShortLink`, `productOfferV2`, `shopOfferV2`, `brandOffer`, `conversionReport`, `validatedReport`.
- **`models.py`**:
  - Dataclasses: `ShortLinkResult`, `ProductOffer`, `ShopOffer`, `ConversionReportItem`, `ConversionReportOrder`, `ConversionReport`, `PageInfo`.
- **`errors.py`**:
  - Exception classes: `ShopeeError`, `ShopeeHTTPError`, `ShopeeAuthError`, `ShopeeRateLimitError`, `ShopeePermissionError`, `ShopeeAPIError`.

---

## 4. Detailed Data Models (`models.py`)

All models implement `.from_dict(d: dict)` and `.to_dict() -> dict`.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class PageInfo:
    page: int | None = None
    limit: int | None = None
    has_next_page: bool | None = None
    scroll_id: str | None = None

@dataclass(slots=True)
class ShortLinkResult:
    short_link: str

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

@dataclass(slots=True)
class ConversionReportOrder:
    order_id: str
    order_status: str
    shop_type: str
    items: list[ConversionReportItem] = field(default_factory=list)

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
```

---

## 5. Client Public API Interface

### 5.1 Synchronous Client
```python
class ShopeeAffiliateClient:
    def __init__(
        self,
        app_id: str,
        secret: str,
        base_url: str = "https://open-api.affiliate.shopee.vn/graphql",
        timeout: float = 30.0,
    ) -> None: ...

    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    def execute(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]: ...

    def generate_short_link(
        self,
        origin_url: str,
        sub_ids: list[str] | None = None,
    ) -> str: ...

    def get_product_offers(
        self,
        keyword: str | None = None,
        item_id: int | None = None,
        shop_id: int | None = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10,
        **extra_vars,
    ) -> tuple[list[ProductOffer], PageInfo]: ...

    def get_shop_offers(
        self,
        keyword: str | None = None,
        shop_id: int | None = None,
        sort_type: int = 1,
        page: int = 1,
        limit: int = 10,
        **extra_vars,
    ) -> tuple[list[ShopOffer], PageInfo]: ...

    def get_conversion_report(
        self,
        purchase_time_start: int | None = None,
        purchase_time_end: int | None = None,
        scroll_id: str | None = None,
        limit: int = 50,
        **extra_vars,
    ) -> tuple[list[ConversionReport], PageInfo]: ...

    def iter_conversion_reports(
        self,
        purchase_time_start: int | None = None,
        purchase_time_end: int | None = None,
        limit_per_page: int = 50,
        max_results: int | None = None,
    ) -> Iterator[ConversionReport]: ...
```

### 5.2 Asynchronous Client
`AsyncShopeeAffiliateClient` mirrors the sync client with `async`/`await` signatures, `async with`, and `async for` in `iter_conversion_reports`.

---

## 6. Error Handling

Shopee Affiliate error code mapping:
- `10020`: `ShopeeAuthError` ("Invalid Signature / Request Expired / Invalid Credential / Invalid Authorization Header")
- `10030`: `ShopeeRateLimitError` ("Rate limit exceeded")
- `10031`, `10033`, `10034`, `10035`: `ShopeePermissionError` ("Access denied / Frozen / Not enrolled in Open API")
- `11000`, `11001`: `ShopeeAPIError` ("Business error / Params error")
- Non-200 HTTP code: `ShopeeHTTPError`
- Network failure / timeouts: `ShopeeHTTPError` (wrapping `httpx.HTTPError`)

---

## 7. Testing Strategy
Using `pytest` and `pytest-asyncio` with `httpx.MockTransport`:
- `test_auth.py`: Validate SHA256 string generation and Authorization header formatting against known reference vector.
- `test_client_sync.py`: Test all client methods against mocked GraphQL endpoints for 200 success and error cases (auth error, business error, invalid payload).
- `test_client_async.py`: Ensure identical test coverage on `AsyncShopeeAffiliateClient`.
- `test_models.py`: Verify serialization and deserialization of dataclasses.
