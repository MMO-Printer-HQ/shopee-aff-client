# Shopee Affiliate Python Client

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, robust Python client library for the [Shopee Affiliate Open API](https://affiliate.shopee.com). Supports both synchronous and asynchronous operations with type annotations, automated SHA-256 signature generation, pagination helpers, structured data models, and comprehensive error mapping.

---

## Features

- **Sync & Async Support**: Both `ShopeeAffiliateClient` and `AsyncShopeeAffiliateClient` powered by `httpx`.
- **Automatic Authentication**: Computes Shopee's HMAC-SHA256 signature and `Authorization` headers seamlessly.
- **Convenient High-Level API**:
  - `generate_short_link`: Generate tracked affiliate short links with sub-IDs.
  - `get_product_offers`: Search and filter affiliate product offers.
  - `get_shop_offers`: Search and filter affiliate shop campaigns.
  - `get_conversion_report` & `iter_conversion_reports`: Query order conversions with automatic scroll-based pagination.
- **Custom GraphQL Execution**: Run arbitrary GraphQL queries and mutations via `client.execute()`.
- **Data Models**: Typed, slot-optimized dataclasses with `.from_dict()` and `.to_dict()` helpers.
- **Precise Error Hierarchy**: Maps Shopee API numeric error codes directly to specialized exceptions (`ShopeeAuthError`, `ShopeeRateLimitError`, `ShopeePermissionError`, etc.).

---

## Requirements

- Python >= 3.11
- `httpx >= 0.24.0`

---

## Installation

Install using `pip`:

```bash
pip install shopee-affiliate
```

Or using `uv`:

```bash
uv add shopee-affiliate
```

---

## Quickstart

### Synchronous Client

```python
from shopee_affiliate import ShopeeAffiliateClient

APP_ID = "your_app_id"
SECRET = "your_secret_key"

# Using client as a context manager automatically manages connection pooling
with ShopeeAffiliateClient(app_id=APP_ID, secret=SECRET) as client:
    # 1. Generate an affiliate short link
    short_link = client.generate_short_link(
        origin_url="https://shopee.vn/product/12345/67890",
        sub_ids=["campaign_summer", "aff_user_1"],
    )
    print(f"Generated Short Link: {short_link}")

    # 2. Query product offers
    products, page_info = client.get_product_offers(
        keyword="wireless headphones",
        limit=5,
        sort_type=1,
    )
    for product in products:
        print(f"[{product.item_id}] {product.product_name} - Commission: {product.commission_rate}%")

    # 3. Query shop offers
    shops, shop_page_info = client.get_shop_offers(
        keyword="official store",
        limit=5,
    )
    for shop in shops:
        print(f"[{shop.shop_id}] {shop.shop_name} - Link: {shop.offer_link}")

    # 4. Fetch a single page of conversion reports
    reports, report_page_info = client.get_conversion_report(
        purchase_time_start=1700000000,
        purchase_time_end=1700086400,
        limit=20,
    )
    for report in reports:
        print(f"Conversion #{report.conversion_id}: Total Commission = {report.total_commission}")
```

### Asynchronous Client

```python
import asyncio
from shopee_affiliate import AsyncShopeeAffiliateClient

APP_ID = "your_app_id"
SECRET = "your_secret_key"

async def main():
    async with AsyncShopeeAffiliateClient(app_id=APP_ID, secret=SECRET) as client:
        # Generate short link asynchronously
        short_link = await client.generate_short_link(
            origin_url="https://shopee.vn/product/12345/67890",
            sub_ids=["async_tag"],
        )
        print(f"Async Short Link: {short_link}")

        # Query product offers
        products, page_info = await client.get_product_offers(
            keyword="mechanical keyboard",
            limit=5,
        )
        for product in products:
            print(f"{product.product_name}: {product.offer_link}")

asyncio.run(main())
```

---

## Pagination with `iter_conversion_reports`

Shopee's conversion report endpoint uses cursor-based pagination with `scrollId`. The client provides an iterator helper that automatically fetches successive pages until results are exhausted or `max_results` is reached.

### Synchronous Pagination

```python
with ShopeeAffiliateClient(app_id=APP_ID, secret=SECRET) as client:
    for report in client.iter_conversion_reports(
        purchase_time_start=1700000000,
        purchase_time_end=1700086400,
        limit_per_page=50,
        max_results=150,  # Stops automatically after 150 records
        order_status="COMPLETED",  # Additional filter parameters forwarded to API
    ):
        print(f"Order #{report.conversion_id} - Commission: {report.total_commission}")
        for order in report.orders:
            for item in order.items:
                print(f"  Item: {item.item_name} (Qty: {item.qty}, Status: {item.display_item_status})")
```

### Asynchronous Pagination

```python
async with AsyncShopeeAffiliateClient(app_id=APP_ID, secret=SECRET) as client:
    async for report in client.iter_conversion_reports(
        purchase_time_start=1700000000,
        purchase_time_end=1700086400,
        limit_per_page=50,
        max_results=100,
    ):
        print(f"Async Conversion #{report.conversion_id}: {report.total_commission}")
```

---

## Custom GraphQL Queries

If you need custom GraphQL fields or queries not covered by high-level methods, use `client.execute()` (or `await client.execute()`):

```python
custom_query = """
query GetCustomOffer($keyword: String, $page: Int, $limit: Int) {
    productOfferV2(keyword: $keyword, page: $page, limit: $limit) {
        nodes {
            itemId
            productName
            commissionRate
        }
        pageInfo {
            page
            limit
            hasNextPage
        }
    }
}
"""

variables = {"keyword": "laptop", "page": 1, "limit": 2}

with ShopeeAffiliateClient(app_id=APP_ID, secret=SECRET) as client:
    data = client.execute(custom_query, variables=variables)
    nodes = data["productOfferV2"]["nodes"]
    print("Custom query result nodes:", nodes)
```

---

## Error Handling

All library exceptions inherit from `ShopeeError`. Numeric API error codes returned by Shopee are automatically mapped into expressive subclasses:

| Exception | Error Code | Description |
|---|---|---|
| `ShopeeAuthError` | `10020` | Signature verification failed or missing authentication. |
| `ShopeeRateLimitError` | `10030` | Rate limit exceeded. |
| `ShopeePermissionError` | `10031`–`10035` | Account lacks permission, unactivated, or frozen. |
| `ShopeeAPIError` | Others | Other Shopee GraphQL business or validation errors. |
| `ShopeeHTTPError` | None | Network failures or non-200 HTTP responses. |

### Example

```python
from shopee_affiliate import (
    ShopeeAffiliateClient,
    ShopeeAuthError,
    ShopeeRateLimitError,
    ShopeePermissionError,
    ShopeeAPIError,
    ShopeeHTTPError,
    ShopeeError,
)

try:
    with ShopeeAffiliateClient(app_id="invalid_id", secret="bad_secret") as client:
        client.generate_short_link("https://shopee.vn/product/1")

except ShopeeAuthError as exc:
    print(f"Authentication failed (code {exc.error_code}): {exc.message}")

except ShopeeRateLimitError as exc:
    print(f"Rate limit exceeded: {exc.message}. Retry after backoff.")

except ShopeePermissionError as exc:
    print(f"Permission denied: {exc.message}")

except ShopeeAPIError as exc:
    print(f"API Error (code {exc.error_code}): {exc.message}")
    print("Raw response payload:", exc.raw_response)

except ShopeeHTTPError as exc:
    print(f"HTTP error {exc.status_code}: {exc.content}")

except ShopeeError as exc:
    print(f"General Shopee client error: {exc}")
```

---

## Authentication Details

Shopee Affiliate Open API requires requests to be authenticated via an HMAC-SHA256 signature in the `Authorization` header:

```http
Authorization: SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}
```

The signature is computed over:
```
signature = HMAC-SHA256(
    key = secret,
    message = app_id + timestamp + payload_json_string
).hexdigest()
```

The library handles payload normalization (compact separators `{"query": ..., "variables": ...}`), timestamp generation, and header formatting automatically.

---

## Data Models

Responses from high-level methods are typed dataclasses:

- **`ShortLinkResult`**: `short_link`
- **`ProductOffer`**: `item_id`, `product_name`, `product_link`, `offer_link`, `image_url`, `commission_rate`, `seller_commission_rate`, `shopee_commission_rate`, `commission`, `price_min`, `price_max`, `sales`, `rating_star`, `shop_id`, `shop_name`, `shop_type`, `product_cat_ids`, etc.
- **`ShopOffer`**: `shop_id`, `shop_name`, `offer_link`, `original_link`, `commission_rate`, `seller_comm_cove_ratio`, `rating_star`, `image_url`, `shop_type`, etc.
- **`ConversionReport`**: `conversion_id`, `purchase_time`, `click_time`, `total_commission`, `seller_commission`, `shopee_commission_capped`, `orders` (list of `ConversionReportOrder` containing `ConversionReportItem`s).
- **`PageInfo`**: `page`, `limit`, `has_next_page`, `scroll_id`.

Every model provides `.from_dict(dict)` for parsing and `.to_dict()` for serializing back to a Python dictionary.

---

## Development & Testing

Run tests using `uv`:

```bash
uv run pytest -v
```

---

## License

This project is licensed under the MIT License.
