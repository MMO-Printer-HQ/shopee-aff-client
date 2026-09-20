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
        try:
            body = response.json()
        except Exception:
            body = {"message": response.text, "raw": response.text}
        return process_graphql_response(response.status_code, body)

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
        **kwargs: Any,
    ) -> Iterator[ConversionReport]:
        """Automatically page through conversion reports using scrollId."""
        if max_results is not None and max_results <= 0:
            return

        current_scroll_id: str | None = None
        count = 0

        while True:
            reports, page_info = self.get_conversion_report(
                purchase_time_start=purchase_time_start,
                purchase_time_end=purchase_time_end,
                limit=limit_per_page,
                scroll_id=current_scroll_id,
                **kwargs,
            )
            if not reports:
                break

            for report in reports:
                yield report
                count += 1
                if max_results is not None and count >= max_results:
                    return

            if not page_info.has_next_page or not page_info.scroll_id:
                break
            current_scroll_id = page_info.scroll_id
