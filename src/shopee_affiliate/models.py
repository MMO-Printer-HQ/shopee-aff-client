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
        raw_page = data.get("page")
        page = int(raw_page) if raw_page is not None and raw_page != "" else None
        raw_limit = data.get("limit")
        limit = int(raw_limit) if raw_limit is not None and raw_limit != "" else None
        return cls(
            page=page,
            limit=limit,
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
        return cls(short_link=str(data.get("shortLink") or ""))

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
        raw_shop_id = data.get("shopId")
        shop_id = int(raw_shop_id) if raw_shop_id is not None and raw_shop_id != "" else None

        raw_start_time = data.get("periodStartTime")
        start_time = int(raw_start_time) if raw_start_time is not None and raw_start_time != "" else None

        raw_end_time = data.get("periodEndTime")
        end_time = int(raw_end_time) if raw_end_time is not None and raw_end_time != "" else None

        return cls(
            item_id=int(data.get("itemId") or 0),
            product_name=str(data.get("productName") or ""),
            product_link=str(data.get("productLink") or ""),
            offer_link=str(data.get("offerLink") or ""),
            image_url=str(data.get("imageUrl") or ""),
            commission_rate=str(data.get("commissionRate") or "0"),
            seller_commission_rate=str(data.get("sellerCommissionRate") or "0"),
            shopee_commission_rate=str(data.get("shopeeCommissionRate") or "0"),
            commission=str(data.get("commission") or "0"),
            price_min=str(data.get("priceMin") or "0"),
            price_max=str(data.get("priceMax") or "0"),
            sales=int(data.get("sales") or 0),
            rating_star=str(data.get("ratingStar") or "0"),
            price_discount_rate=int(data.get("priceDiscountRate") or 0),
            shop_id=shop_id,
            shop_name=str(data.get("shopName") or ""),
            shop_type=data.get("shopType") or [],
            product_cat_ids=data.get("productCatIds") or [],
            period_start_time=start_time,
            period_end_time=end_time,
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
        raw_start_time = data.get("periodStartTime")
        start_time = int(raw_start_time) if raw_start_time is not None and raw_start_time != "" else None

        raw_end_time = data.get("periodEndTime")
        end_time = int(raw_end_time) if raw_end_time is not None and raw_end_time != "" else None

        return cls(
            shop_id=int(data.get("shopId") or 0),
            shop_name=str(data.get("shopName") or ""),
            offer_link=str(data.get("offerLink") or ""),
            original_link=str(data.get("originalLink") or ""),
            commission_rate=str(data.get("commissionRate") or "0"),
            seller_comm_cove_ratio=str(data.get("sellerCommCoveRatio") or "0"),
            rating_star=str(data.get("ratingStar") or "0"),
            image_url=str(data.get("imageUrl") or ""),
            shop_type=data.get("shopType") or [],
            period_start_time=start_time,
            period_end_time=end_time,
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
        raw_shop_id = data.get("shopId")
        shop_id = int(raw_shop_id) if raw_shop_id is not None and raw_shop_id != "" else None

        raw_complete_time = data.get("completeTime")
        complete_time = int(raw_complete_time) if raw_complete_time is not None and raw_complete_time != "" else None

        return cls(
            item_id=int(data.get("itemId") or 0),
            item_name=str(data.get("itemName") or ""),
            item_price=str(data.get("itemPrice") or "0"),
            qty=int(data.get("qty") or 0),
            actual_amount=str(data.get("actualAmount") or "0"),
            item_total_commission=str(data.get("itemTotalCommission") or "0"),
            item_seller_commission=str(data.get("itemSellerCommission") or "0"),
            item_shopee_commission_capped=str(data.get("itemShopeeCommissionCapped") or "0"),
            display_item_status=str(data.get("displayItemStatus") or ""),
            order_id=str(data.get("orderId") or ""),
            shop_id=shop_id,
            shop_name=str(data.get("shopName") or ""),
            complete_time=complete_time,
            image_url=str(data.get("imageUrl") or ""),
            fraud_status=str(data.get("fraudStatus") or ""),
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
            order_id=str(data.get("orderId") or ""),
            order_status=str(data.get("orderStatus") or ""),
            shop_type=str(data.get("shopType") or ""),
            items=[ConversionReportItem.from_dict(item) for item in raw_items if isinstance(item, dict)],
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
            conversion_id=int(data.get("conversionId") or 0),
            purchase_time=int(data.get("purchaseTime") or 0),
            click_time=int(data.get("clickTime") or 0),
            total_commission=str(data.get("totalCommission") or "0"),
            seller_commission=str(data.get("sellerCommission") or "0"),
            shopee_commission_capped=str(data.get("shopeeCommissionCapped") or "0"),
            net_commission=str(data.get("netCommission") or ""),
            buyer_type=str(data.get("buyerType") or ""),
            utm_content=str(data.get("utmContent") or ""),
            device=str(data.get("device") or ""),
            orders=[ConversionReportOrder.from_dict(order) for order in raw_orders if isinstance(order, dict)],
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
