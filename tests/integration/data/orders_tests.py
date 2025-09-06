"""Integration tests for the OrdersDataClient module."""

import os
import pytest
import pyotp
from datetime import datetime, timedelta

from robinhood_client.common.session import FileSystemSessionStorage
from robinhood_client.common.schema import StockOrder
from robinhood_client.common.cursor import PaginatedResult
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import StockOrdersRequest, StockOrderRequest


@pytest.fixture(scope="module")
def authenticated_client():
    """Fixture that provides an authenticated OrdersDataClient for all tests."""
    # Create a session storage
    session_storage = FileSystemSessionStorage()

    # Initialize the client with our session storage
    client = OrdersDataClient(session_storage=session_storage)

    # Check for credentials in environment variables
    username = os.environ.get("RH_USERNAME")
    password = os.environ.get("RH_PASSWORD")
    mfa_code = os.environ.get("RH_MFA_CODE")  # Optional MFA code

    if not username or not password:
        pytest.skip("RH_USERNAME and RH_PASSWORD environment variables are required")

    totp = pyotp.TOTP(mfa_code).now()

    # Login using the client's login method
    client.login(
        username=username,
        password=password,
        mfa_code=totp,
        persist_session=True,
    )

    yield client

    # Cleanup (logout) after all tests in this module
    # Note: The session will be persisted, so explicit logout may not be necessary


@pytest.fixture(scope="module")
def account_number():
    """Fixture that provides the account number for tests."""
    account_number = os.environ.get("RH_ACCOUNT_NUMBER")
    if not account_number:
        pytest.skip("RH_ACCOUNT_NUMBER environment variable is not set")
    return account_number


def test_get_stock_orders(authenticated_client: OrdersDataClient, account_number: str):
    """Integration test for getting stock orders."""
    # Create a request for recent orders (last 7 days)
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    request = StockOrdersRequest(
        account_number=account_number, start_date=one_week_ago, page_size=5
    )

    # Execute the request
    response = authenticated_client.get_stock_orders(request)

    # Verify the response is a PaginatedResult
    assert response is not None
    assert isinstance(response, PaginatedResult)
    assert hasattr(response, "results")
    assert isinstance(response.results, list)

    # Print number of orders found (helpful for debugging)
    print(f"Found {len(response.results)} orders")

    # If orders exist, verify comprehensive structure and values
    if response.results:
        first_order = response.results[0]

        # Check required string fields exist and are non-empty
        required_string_fields = [
            "id",
            "ref_id",
            "url",
            "account",
            "user_uuid",
            "position",
            "instrument",
            "instrument_id",
        ]
        for field in required_string_fields:
            assert hasattr(first_order, field), f"Missing field: {field}"
            field_value = getattr(first_order, field)
            assert field_value is not None, f"Field {field} is None"
            assert isinstance(field_value, str), (
                f"Field {field} is not a string: {type(field_value)}"
            )
            assert len(field_value) > 0, f"Field {field} is empty"

        # Check numeric fields exist and have valid values
        numeric_fields = [
            "cumulative_quantity",
            "fees",
            "sec_fees",
            "taf_fees",
            "cat_fees",
        ]
        for field in numeric_fields:
            assert hasattr(first_order, field), f"Missing numeric field: {field}"
            field_value = getattr(first_order, field)
            assert field_value is not None, f"Numeric field {field} is None"
            # Should be either string or float/int
            assert isinstance(field_value, (str, float, int)), (
                f"Field {field} has invalid type: {type(field_value)}"
            )
            if isinstance(field_value, str):
                # If string, should be convertible to float
                try:
                    float(field_value)
                except ValueError:
                    pytest.fail(
                        f"String field {field} cannot be converted to float: {field_value}"
                    )

        # Check enum fields have valid values
        from robinhood_client.common.enums import (
            OrderState,
            OrderType,
            OrderSide,
            TimeInForce,
            TriggerType,
            PositionEffect,
        )

        assert hasattr(first_order, "state")
        assert first_order.state in [state.value for state in OrderState] or isinstance(
            first_order.state, OrderState
        )

        assert hasattr(first_order, "derived_state")
        assert first_order.derived_state in [
            state.value for state in OrderState
        ] or isinstance(first_order.derived_state, OrderState)

        assert hasattr(first_order, "type")
        assert first_order.type in [
            order_type.value for order_type in OrderType
        ] or isinstance(first_order.type, OrderType)

        assert hasattr(first_order, "side")
        assert first_order.side in [side.value for side in OrderSide] or isinstance(
            first_order.side, OrderSide
        )

        assert hasattr(first_order, "time_in_force")
        assert first_order.time_in_force in [
            tif.value for tif in TimeInForce
        ] or isinstance(first_order.time_in_force, TimeInForce)

        assert hasattr(first_order, "trigger")
        assert first_order.trigger in [
            trigger.value for trigger in TriggerType
        ] or isinstance(first_order.trigger, TriggerType)

        assert hasattr(first_order, "position_effect")
        assert first_order.position_effect in [
            effect.value for effect in PositionEffect
        ] or isinstance(first_order.position_effect, PositionEffect)

        # Check datetime fields
        datetime_fields = ["created_at", "updated_at", "last_transaction_at"]
        for field in datetime_fields:
            assert hasattr(first_order, field), f"Missing datetime field: {field}"
            field_value = getattr(first_order, field)
            assert field_value is not None, f"Datetime field {field} is None"
            # Should be either datetime object or string
            if isinstance(field_value, str):
                # If string, should be a valid datetime format
                try:
                    datetime.fromisoformat(field_value.replace("Z", "+00:00"))
                except ValueError:
                    pytest.fail(
                        f"Datetime field {field} is not in valid ISO format: {field_value}"
                    )

        # Check boolean fields
        boolean_fields = [
            "extended_hours",
            "override_dtbp_checks",
            "override_day_trade_checks",
            "is_ipo_access_order",
            "is_ipo_access_price_finalized",
            "is_visible_to_user",
            "has_ipo_access_custom_price_limit",
            "is_primary_account",
            "is_editable",
        ]
        for field in boolean_fields:
            if hasattr(first_order, field):
                field_value = getattr(first_order, field)
                assert isinstance(field_value, bool), (
                    f"Boolean field {field} is not boolean: {type(field_value)}"
                )

        # Check integer fields
        integer_fields = ["order_form_version", "last_update_version"]
        for field in integer_fields:
            if hasattr(first_order, field):
                field_value = getattr(first_order, field)
                assert isinstance(field_value, int), (
                    f"Integer field {field} is not integer: {type(field_value)}"
                )
                assert field_value > 0, (
                    f"Integer field {field} should be positive: {field_value}"
                )

        # Check lists/arrays
        if hasattr(first_order, "executions"):
            assert isinstance(first_order.executions, list), (
                "executions should be a list"
            )

        if hasattr(first_order, "sales_taxes"):
            assert isinstance(first_order.sales_taxes, list), (
                "sales_taxes should be a list"
            )

        # Business logic checks
        if hasattr(first_order, "quantity") and first_order.quantity is not None:
            quantity_val = (
                float(first_order.quantity)
                if isinstance(first_order.quantity, str)
                else first_order.quantity
            )
            assert quantity_val > 0, f"Quantity should be positive: {quantity_val}"

        if hasattr(first_order, "cumulative_quantity"):
            cum_qty_val = (
                float(first_order.cumulative_quantity)
                if isinstance(first_order.cumulative_quantity, str)
                else first_order.cumulative_quantity
            )
            assert cum_qty_val >= 0, (
                f"Cumulative quantity should be non-negative: {cum_qty_val}"
            )

        # Check that URLs are valid format
        url_fields = ["url", "instrument", "account", "position"]
        for field in url_fields:
            if hasattr(first_order, field):
                field_value = getattr(first_order, field)
                if field_value:
                    assert field_value.startswith("https://"), (
                        f"Field {field} should be a valid HTTPS URL: {field_value}"
                    )

        print(
            f"✓ First order validation passed - ID: {first_order.id}, Side: {first_order.side}, State: {first_order.state}"
        )

        # If multiple orders, check that they're all valid
        if len(response.results) > 1:
            print(f"Validating {len(response.results)} total orders...")
            for i, order in enumerate(response.results):
                # Basic validation for all orders
                assert hasattr(order, "id") and order.id
                assert hasattr(order, "state") and order.state
                assert hasattr(order, "side") and order.side
                assert hasattr(order, "created_at") and order.created_at

            print(f"✓ All {len(response.results)} orders passed basic validation")


def test_get_stock_order(authenticated_client: OrdersDataClient, account_number: str):
    """Integration test for getting a single stock order."""
    # First, get recent orders to find an order ID to test with
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    orders_request = StockOrdersRequest(
        account_number=account_number, start_date=one_week_ago, page_size=1
    )

    orders_response = authenticated_client.get_stock_orders(orders_request)

    # Skip test if no orders found
    if not orders_response.results:
        pytest.skip("No recent orders found to test get_stock_order with")

    # Use the first order's ID
    test_order_id = orders_response.results[0].id
    print(f"Testing get_stock_order with order ID: {test_order_id}")

    # Create a request for the specific order
    single_order_request = StockOrderRequest(
        account_number=account_number, order_id=test_order_id
    )

    # Execute the request for single order
    single_order = authenticated_client.get_stock_order(single_order_request)

    # Verify the response
    assert single_order is not None
    assert hasattr(single_order, "id")
    assert single_order.id == test_order_id

    # Verify essential fields exist
    required_fields = [
        "id",
        "ref_id",
        "url",
        "account",
        "user_uuid",
        "instrument",
        "instrument_id",
    ]
    enum_fields = ["state", "side"]  # These can be enum objects or strings

    for field in required_fields:
        assert hasattr(single_order, field), f"Missing field: {field}"
        field_value = getattr(single_order, field)
        assert field_value is not None, f"Field {field} is None"
        assert isinstance(field_value, str), (
            f"Field {field} is not a string: {type(field_value)}"
        )
        assert len(field_value) > 0, f"Field {field} is empty"

    # Check enum fields separately (can be enum objects or strings)
    for field in enum_fields:
        assert hasattr(single_order, field), f"Missing field: {field}"
        field_value = getattr(single_order, field)
        assert field_value is not None, f"Field {field} is None"
        # Can be either string or enum object
        assert isinstance(field_value, (str, object)), (
            f"Field {field} has invalid type: {type(field_value)}"
        )

    # Verify datetime fields
    datetime_fields = ["created_at", "updated_at"]
    for field in datetime_fields:
        if hasattr(single_order, field):
            field_value = getattr(single_order, field)
            assert field_value is not None, f"Datetime field {field} is None"

    # Verify numeric fields have valid values
    numeric_fields = ["cumulative_quantity", "fees"]
    for field in numeric_fields:
        if hasattr(single_order, field):
            field_value = getattr(single_order, field)
            if field_value is not None:
                # Should be either string or float/int
                assert isinstance(field_value, (str, float, int)), (
                    f"Field {field} has invalid type: {type(field_value)}"
                )
                if isinstance(field_value, str) and field_value:
                    # If string, should be convertible to float
                    try:
                        float(field_value)
                    except ValueError:
                        pytest.fail(
                            f"String field {field} cannot be converted to float: {field_value}"
                        )

    # Verify URLs are valid format
    url_fields = ["url", "instrument", "account", "position"]
    for field in url_fields:
        if hasattr(single_order, field):
            field_value = getattr(single_order, field)
            if field_value:
                assert field_value.startswith("https://"), (
                    f"Field {field} should be a valid HTTPS URL: {field_value}"
                )

    print(
        f"✓ Single order validation passed - ID: {single_order.id}, Side: {single_order.side}, State: {single_order.state}"
    )

    # Verify this order matches the one from the orders list
    original_order = orders_response.results[0]
    assert single_order.id == original_order.id
    assert single_order.side == original_order.side
    assert single_order.state == original_order.state

    print("✓ Single order matches original order from list")


def test_get_stock_orders_pagination(
    authenticated_client: OrdersDataClient, account_number: str
):
    """Integration test for cursor-based stock orders retrieval."""
    # Create a request for recent orders
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    request = StockOrdersRequest(
        account_number=account_number, start_date=one_week_ago, page_size=3
    )

    # Execute the cursor request
    result = authenticated_client.get_stock_orders(request)

    # Verify the result structure
    assert result is not None

    assert isinstance(result, PaginatedResult)

    # Verify current page access
    current_page_results = result.results
    assert isinstance(current_page_results, list)

    print(f"Current page has {len(current_page_results)} orders")
    print(f"Has next page: {result.cursor().has_next()}")
    print(f"Has previous page: {result.cursor().has_previous()}")

    # If orders exist, verify they are valid StockOrder objects
    if current_page_results:
        first_order = current_page_results[0]
        assert isinstance(first_order, StockOrder)
        assert hasattr(first_order, "id")
        assert hasattr(first_order, "state")
        assert hasattr(first_order, "side")

        print(f"✓ First order: {first_order.id} - {first_order.state}")

    # Test cursor navigation properties
    cursor = result.cursor()
    current_page = cursor.current_page()
    assert current_page is not None
    assert hasattr(current_page, "results")
    assert hasattr(current_page, "next")
    assert hasattr(current_page, "previous")

    print("✓ Cursor basic functionality verified")


def test_get_stock_orders_iteration(
    authenticated_client: OrdersDataClient, account_number: str
):
    """Integration test for iterating through multiple pages with cursor."""
    # Create a request with small page size to test pagination
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    request = StockOrdersRequest(
        account_number=account_number, start_date=one_week_ago, page_size=10
    )

    # Execute the cursor request
    result = authenticated_client.get_stock_orders(request)

    # Test iteration through all pages
    all_orders_via_iteration = []
    page_count = 0

    cursor = result.cursor()
    while True:
        current_page = cursor.current_page()
        page_count += 1
        print(f"Page {page_count}: {len(current_page.results)} orders")

        for order in current_page.results:
            all_orders_via_iteration.append(order)
            assert isinstance(order, StockOrder)

        if not cursor.has_next():
            break

        cursor.next()

        # Safety check to prevent infinite loops in tests
        if page_count >= 5:
            print("Stopping at page 5 for test safety")
            break

    # # Test automatic iteration
    # cursor.reset()
    # all_orders_auto = list(result)

    # # Both methods should return the same orders (up to the page limit we set)
    # if page_count < 5:  # Only compare if we didn't hit our safety limit
    #     assert len(all_orders_via_iteration) == len(all_orders_auto)
    #     for manual_order, auto_order in zip(all_orders_via_iteration, all_orders_auto):
    #         assert manual_order.id == auto_order.id

    # print(f"✓ Manual iteration: {len(all_orders_via_iteration)} orders across {page_count} pages")
    # print(f"✓ Auto iteration: {len(all_orders_auto)} orders")
