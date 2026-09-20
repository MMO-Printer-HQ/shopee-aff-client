"""Tests for Shopee Affiliate models and error hierarchy."""

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
    ShopeeHTTPError,
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
    assert offer.to_dict()["itemId"] == 12345


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
    dict_repr = report.to_dict()
    assert dict_repr["conversionId"] == 987654321
    assert dict_repr["orders"][0]["orderId"] == "ORD123"
    assert dict_repr["orders"][0]["items"][0]["itemId"] == 111


def test_page_info_model():
    data = {
        "page": 1,
        "limit": 20,
        "hasNextPage": True,
        "scrollId": "scroll-token-123",
    }
    page_info = PageInfo.from_dict(data)
    assert page_info.page == 1
    assert page_info.limit == 20
    assert page_info.has_next_page is True
    assert page_info.scroll_id == "scroll-token-123"
    assert page_info.to_dict() == data


def test_shop_offer_model():
    data = {
        "shopId": 1234,
        "shopName": "Official Store",
        "offerLink": "https://shope.ee/shop123",
        "originalLink": "https://shopee.vn/shop123",
        "commissionRate": "0.10",
        "sellerCommCoveRatio": "1.0",
        "ratingStar": "4.9",
        "imageUrl": "https://cf.shopee.vn/img.png",
        "shopType": [1],
        "periodStartTime": 1700000000,
        "periodEndTime": 1700100000,
    }
    shop_offer = ShopOffer.from_dict(data)
    assert shop_offer.shop_id == 1234
    assert shop_offer.shop_name == "Official Store"
    assert shop_offer.to_dict() == data


def test_error_mapping():
    err_auth = map_shopee_error(10020, "Invalid signature")
    assert isinstance(err_auth, ShopeeAuthError)
    assert str(err_auth) == "[10020] Invalid signature"

    err_limit = map_shopee_error(10030, "Rate limit")
    assert isinstance(err_limit, ShopeeRateLimitError)

    err_perm = map_shopee_error(10031, "Access denied")
    assert isinstance(err_perm, ShopeePermissionError)

    err_perm_other = map_shopee_error(10035, "Account frozen")
    assert isinstance(err_perm_other, ShopeePermissionError)

    err_api = map_shopee_error(11000, "General business error")
    assert isinstance(err_api, ShopeeAPIError)


def test_shopee_error_base():
    err_simple = ShopeeError("Simple error")
    assert str(err_simple) == "Simple error"
    assert err_simple.error_code is None
    assert err_simple.raw_response == {}

    http_err = ShopeeHTTPError("Network down", status_code=502, content="Bad Gateway")
    assert isinstance(http_err, ShopeeError)
    assert http_err.status_code == 502
    assert http_err.content == "Bad Gateway"
