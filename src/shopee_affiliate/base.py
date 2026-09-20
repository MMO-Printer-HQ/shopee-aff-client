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
        if isinstance(first_error, dict):
            code = first_error.get("code")
            message = first_error.get("message") or str(first_error)
            if isinstance(code, (int, str)):
                try:
                    int_code = int(code)
                    raise map_shopee_error(int_code, message, raw_response=response_json)
                except ValueError:
                    pass
            raise ShopeeAPIError(message, raw_response=response_json)
        else:
            raise ShopeeAPIError(str(first_error), raw_response=response_json)

    # Check top-level error code if present
    code = response_json.get("code")
    if code is not None and code != 0:
        message = response_json.get("message", "Unknown error")
        raise map_shopee_error(int(code), message, raw_response=response_json)

    data = response_json.get("data")
    if data is None:
        raise ShopeeAPIError("Missing 'data' field in response", raw_response=response_json)

    return data
