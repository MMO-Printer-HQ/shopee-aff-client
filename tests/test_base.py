import pytest
from shopee_affiliate.base import serialize_graphql_payload, process_graphql_response
from shopee_affiliate.errors import ShopeeAuthError, ShopeeAPIError, ShopeeHTTPError
from shopee_affiliate.queries import (
    GENERATE_SHORT_LINK_MUTATION,
    PRODUCT_OFFER_QUERY,
    SHOP_OFFER_QUERY,
    CONVERSION_REPORT_QUERY,
    VALIDATED_REPORT_QUERY,
)


def test_serialize_graphql_payload():
    query = "query { test }"
    payload = serialize_graphql_payload(query, {"foo": "bar"})
    assert '"query":"query { test }"' in payload
    assert '"variables":{"foo":"bar"}' in payload


def test_serialize_graphql_payload_without_variables():
    query = "query { test }"
    payload = serialize_graphql_payload(query)
    assert '"query":"query { test }"' in payload
    assert "variables" not in payload


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


def test_process_graphql_response_error_without_code():
    data = {
        "errors": [{"message": "Syntax error"}],
    }
    with pytest.raises(ShopeeAPIError) as exc_info:
        process_graphql_response(200, data)
    assert "Syntax error" in str(exc_info.value)


def test_process_graphql_response_non_dict_error():
    data = {
        "errors": ["Internal Server Error"],
    }
    with pytest.raises(ShopeeAPIError) as exc_info:
        process_graphql_response(200, data)
    assert "Internal Server Error" in str(exc_info.value)
    assert exc_info.value.raw_response == data


def test_process_graphql_response_string_code():
    data = {
        "errors": [{"message": "Invalid credential", "code": "10020"}],
    }
    with pytest.raises(ShopeeAuthError) as exc_info:
        process_graphql_response(200, data)
    assert exc_info.value.error_code == 10020


def test_process_graphql_response_unparseable_code():
    data = {
        "errors": [{"message": "Bad request", "code": "NOT_AN_INT"}],
    }
    with pytest.raises(ShopeeAPIError) as exc_info:
        process_graphql_response(200, data)
    assert "Bad request" in str(exc_info.value)


def test_process_graphql_response_top_level_code():
    data = {
        "code": 10020,
        "message": "Top level auth error",
    }
    with pytest.raises(ShopeeAuthError) as exc_info:
        process_graphql_response(200, data)
    assert exc_info.value.error_code == 10020


def test_process_graphql_response_missing_data():
    data = {"code": 0}
    with pytest.raises(ShopeeAPIError) as exc_info:
        process_graphql_response(200, data)
    assert "Missing 'data' field" in str(exc_info.value)


def test_process_graphql_response_http_error():
    with pytest.raises(ShopeeHTTPError):
        process_graphql_response(500, {})


def test_queries_defined():
    assert "generateShortLink" in GENERATE_SHORT_LINK_MUTATION
    assert "productOfferV2" in PRODUCT_OFFER_QUERY
    assert "shopOfferV2" in SHOP_OFFER_QUERY
    assert "conversionReport" in CONVERSION_REPORT_QUERY
    assert "validatedReport" in VALIDATED_REPORT_QUERY
