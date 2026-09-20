"""Tests for asynchronous AsyncShopeeAffiliateClient."""

import json
import httpx
import pytest

from shopee_affiliate.async_client import AsyncShopeeAffiliateClient
from shopee_affiliate.errors import ShopeeAuthError, ShopeeHTTPError
from shopee_affiliate.models import (
    ConversionReport,
    PageInfo,
    ProductOffer,
    ShopOffer,
)


def mock_transport_handler(request: httpx.Request) -> httpx.Response:
    auth_header = request.headers.get("Authorization", "")
    assert auth_header.startswith("SHA256 Credential="), f"Invalid auth header: {auth_header}"

    body = json.loads(request.content.decode("utf-8"))
    query = body.get("query", "")
    variables = body.get("variables", {})

    if "generateShortLink" in query:
        origin_url = variables.get("input", {}).get("originUrl", "")
        if "invalid" in origin_url:
            return httpx.Response(
                200,
                json={"errors": [{"code": 10001, "message": "Invalid origin url"}]},
            )
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
                                "productName": "Async Mock Item",
                                "productLink": "https://shopee.vn/async_mock",
                                "offerLink": "https://shope.ee/async_mock",
                                "commissionRate": "0.20",
                            }
                        ],
                        "pageInfo": {"page": 1, "limit": 10, "hasNextPage": False},
                    }
                }
            },
        )

    if "shopOfferV2" in query:
        return httpx.Response(
            200,
            json={
                "data": {
                    "shopOfferV2": {
                        "nodes": [
                            {
                                "shopId": 88888,
                                "shopName": "Async Store",
                                "offerLink": "https://shope.ee/async_shop",
                                "originalLink": "https://shopee.vn/async_shop",
                                "commissionRate": "0.12",
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

    if "errorAuth" in query:
        return httpx.Response(
            200,
            json={"errors": [{"code": 10020, "message": "Signature verification failed"}]},
        )

    if "http500" in query:
        return httpx.Response(500, json={"message": "Internal Server Error"})

    if "http502_html" in query:
        return httpx.Response(502, text="<html><body>502 Bad Gateway</body></html>")

    return httpx.Response(400, json={"message": "Not Found"})


@pytest.mark.asyncio
async def test_async_generate_short_link():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        link = await client.generate_short_link("https://shopee.vn/item-1", sub_ids=["sub1", "sub2"])
        assert link == "https://shope.ee/async_mocked"

        link_no_sub = await client.generate_short_link("https://shopee.vn/item-2")
        assert link_no_sub == "https://shope.ee/async_mocked"


@pytest.mark.asyncio
async def test_async_get_product_offers():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        offers, page_info = await client.get_product_offers(
            keyword="Async Item",
            item_id=54321,
            shop_id=99,
            product_cat_id=10,
            list_type=0,
            sort_type=1,
            page=1,
            limit=10,
            is_ams_offer=True,
            is_key_seller=False,
        )
        assert len(offers) == 1
        assert isinstance(offers[0], ProductOffer)
        assert offers[0].item_id == 54321
        assert offers[0].product_name == "Async Mock Item"
        assert offers[0].commission_rate == "0.20"
        assert isinstance(page_info, PageInfo)
        assert page_info.has_next_page is False


@pytest.mark.asyncio
async def test_async_get_shop_offers():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        offers, page_info = await client.get_shop_offers(
            keyword="Async Store",
            shop_id=88888,
            shop_type=[1],
            is_key_seller=True,
            sort_type=1,
            page=1,
            limit=10,
        )
        assert len(offers) == 1
        assert isinstance(offers[0], ShopOffer)
        assert offers[0].shop_id == 88888
        assert offers[0].shop_name == "Async Store"
        assert isinstance(page_info, PageInfo)
        assert page_info.has_next_page is False


@pytest.mark.asyncio
async def test_async_get_conversion_report():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        reports, page_info = await client.get_conversion_report(
            purchase_time_start=1700000000,
            purchase_time_end=1700086400,
            complete_time_start=1700000000,
            complete_time_end=1700086400,
            shop_name="Mock Shop",
            shop_id=111,
            order_id="ORD123",
            order_status="COMPLETED",
            limit=10,
        )
        assert len(reports) == 1
        assert isinstance(reports[0], ConversionReport)
        assert reports[0].conversion_id == 888
        assert page_info.scroll_id == "scroll_async_123"


@pytest.mark.asyncio
async def test_async_iter_conversion_reports():
    calls = []

    def paging_transport_handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        variables = body.get("variables", {})
        calls.append(variables)
        scroll_id = variables.get("scrollId")

        if scroll_id is None:
            return httpx.Response(
                200,
                json={
                    "data": {
                        "conversionReport": {
                            "nodes": [{"conversionId": 201, "totalCommission": "100"}],
                            "pageInfo": {"limit": 1, "hasNextPage": True, "scrollId": "async_page2"},
                        }
                    }
                },
            )
        elif scroll_id == "async_page2":
            return httpx.Response(
                200,
                json={
                    "data": {
                        "conversionReport": {
                            "nodes": [{"conversionId": 202, "totalCommission": "200"}],
                            "pageInfo": {"limit": 1, "hasNextPage": False, "scrollId": "async_page3"},
                        }
                    }
                },
            )
        return httpx.Response(400, json={"message": "Unexpected scrollId"})

    mock_transport = httpx.MockTransport(paging_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        items = []
        async for report in client.iter_conversion_reports(limit_per_page=1, order_status="COMPLETED"):
            items.append(report)
        assert len(items) == 2
        assert items[0].conversion_id == 201
        assert items[1].conversion_id == 202
        # Verify kwargs forwarding:
        assert calls[0].get("orderStatus") == "COMPLETED"
        assert calls[1].get("orderStatus") == "COMPLETED"
        # Verify early termination on hasNextPage=False: exactly 2 calls made, async_page3 not called
        assert len(calls) == 2

    # Test max_results capping
    calls.clear()
    mock_transport = httpx.MockTransport(paging_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        items = []
        async for report in client.iter_conversion_reports(limit_per_page=1, max_results=1):
            items.append(report)
        assert len(items) == 1
        assert items[0].conversion_id == 201
        assert len(calls) == 1


@pytest.mark.asyncio
async def test_async_error_handling():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    async with AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport) as client:
        with pytest.raises(ShopeeAuthError) as exc_info:
            await client.execute("query errorAuth { dummy }")
        assert exc_info.value.error_code == 10020

        with pytest.raises(ShopeeHTTPError) as exc_info_http:
            await client.execute("query http500 { dummy }")
        assert exc_info_http.value.status_code == 500

        with pytest.raises(ShopeeHTTPError) as exc_info_http_html:
            await client.execute("query http502_html { dummy }")
        assert exc_info_http_html.value.status_code == 502


@pytest.mark.asyncio
async def test_async_context_manager():
    mock_transport = httpx.MockTransport(mock_transport_handler)
    client = AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport)
    async with client as ctx:
        assert ctx is client
        assert not client._http.is_closed
    assert client._http.is_closed

    # Direct aclose test
    client2 = AsyncShopeeAffiliateClient(app_id="app1", secret="sec1", transport=mock_transport)
    assert not client2._http.is_closed
    await client2.aclose()
    assert client2._http.is_closed
