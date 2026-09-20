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
