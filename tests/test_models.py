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


def test_product_offer_model_null_values():
    data = {
        "itemId": None,
        "productName": None,
        "productLink": None,
        "offerLink": None,
        "imageUrl": None,
        "commissionRate": None,
        "sellerCommissionRate": None,
        "shopeeCommissionRate": None,
        "commission": None,
        "priceMin": None,
        "priceMax": None,
        "sales": None,
        "ratingStar": None,
        "priceDiscountRate": None,
        "shopId": None,
        "shopName": None,
        "shopType": None,
        "productCatIds": None,
        "periodStartTime": None,
        "periodEndTime": None,
    }
    offer = ProductOffer.from_dict(data)
    assert offer.item_id == 0
    assert offer.product_name == ""
    assert offer.product_link == ""
    assert offer.offer_link == ""
    assert offer.image_url == ""
    assert offer.commission_rate == "0"
    assert offer.seller_commission_rate == "0"
    assert offer.shopee_commission_rate == "0"
    assert offer.commission == "0"
    assert offer.price_min == "0"
    assert offer.price_max == "0"
    assert offer.sales == 0
    assert offer.rating_star == "0"
    assert offer.price_discount_rate == 0
    assert offer.shop_id is None
    assert offer.shop_name == ""
    assert offer.shop_type == []
    assert offer.product_cat_ids == []
    assert offer.period_start_time is None
    assert offer.period_end_time is None


def test_shop_offer_model_null_values():
    data = {
        "shopId": None,
        "shopName": None,
        "offerLink": None,
        "originalLink": None,
        "commissionRate": None,
        "sellerCommCoveRatio": None,
        "ratingStar": None,
        "imageUrl": None,
        "shopType": None,
        "periodStartTime": None,
        "periodEndTime": None,
    }
    offer = ShopOffer.from_dict(data)
    assert offer.shop_id == 0
    assert offer.shop_name == ""
    assert offer.offer_link == ""
    assert offer.original_link == ""
    assert offer.commission_rate == "0"
    assert offer.seller_comm_cove_ratio == "0"
    assert offer.rating_star == "0"
    assert offer.image_url == ""
    assert offer.shop_type == []
    assert offer.period_start_time is None
    assert offer.period_end_time is None


def test_conversion_report_item_null_values():
    data = {
        "itemId": None,
        "itemName": None,
        "itemPrice": None,
        "qty": None,
        "actualAmount": None,
        "itemTotalCommission": None,
        "itemSellerCommission": None,
        "itemShopeeCommissionCapped": None,
        "displayItemStatus": None,
        "orderId": None,
        "shopId": None,
        "shopName": None,
        "completeTime": None,
        "imageUrl": None,
        "fraudStatus": None,
    }
    item = ConversionReportItem.from_dict(data)
    assert item.item_id == 0
    assert item.item_name == ""
    assert item.item_price == "0"
    assert item.qty == 0
    assert item.actual_amount == "0"
    assert item.item_total_commission == "0"
    assert item.item_seller_commission == "0"
    assert item.item_shopee_commission_capped == "0"
    assert item.display_item_status == ""
    assert item.order_id == ""
    assert item.shop_id is None
    assert item.shop_name == ""
    assert item.complete_time is None
    assert item.image_url == ""
    assert item.fraud_status == ""


def test_conversion_report_null_values():
    data = {
        "conversionId": None,
        "purchaseTime": None,
        "clickTime": None,
        "totalCommission": None,
        "sellerCommission": None,
        "shopeeCommissionCapped": None,
        "netCommission": None,
        "buyerType": None,
        "utmContent": None,
        "device": None,
        "orders": None,
    }
    report = ConversionReport.from_dict(data)
    assert report.conversion_id == 0
    assert report.purchase_time == 0
    assert report.click_time == 0
    assert report.total_commission == "0"
    assert report.seller_commission == "0"
    assert report.shopee_commission_capped == "0"
    assert report.net_commission == ""
    assert report.buyer_type == ""
    assert report.utm_content == ""
    assert report.device == ""
    assert report.orders == []


def test_page_info_and_short_link_null_values():
    page_info = PageInfo.from_dict({"page": None, "limit": None, "hasNextPage": None, "scrollId": None})
    assert page_info.page is None
    assert page_info.limit is None
    assert page_info.has_next_page is None
    assert page_info.scroll_id is None

    short_link = ShortLinkResult.from_dict({"shortLink": None})
    assert short_link.short_link == ""


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
