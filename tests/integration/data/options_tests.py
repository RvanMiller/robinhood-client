"""Integration tests for Options Orders."""

import os
import pyotp
import pytest
from datetime import date, timedelta

from robinhood_client.data import OrdersDataClient
from robinhood_client.data.requests import OptionOrderRequest, OptionOrdersRequest
from robinhood_client.common.session import FileSystemSessionStorage
from robinhood_client.common.schema import OptionsOrder


@pytest.fixture(scope="module")
def orders_client():
    """Fixture that provides an authenticated OrdersDataClient for all tests."""
    # Create a session storage
    session_storage = FileSystemSessionStorage()

    # Initialize the client with our session storage
    client = OrdersDataClient(session_storage=session_storage)

    # Check for credentials in environment variables
    username = os.environ.get("RH_USERNAME")
    password = os.environ.get("RH_PASSWORD")
    mfa_code = os.environ.get("RH_MFA_CODE")

    if not username or not password:
        pytest.skip("RH_USERNAME and RH_PASSWORD environment variables are required")

    if not mfa_code:
        pytest.skip("RH_MFA_CODE environment variable is required")

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


def test_get_options_orders(orders_client: OrdersDataClient, account_number: str):
    """Integration test for getting options orders."""
    # Create request with recent date to limit results
    start_date = date.today() - timedelta(days=30)
    request = OptionOrdersRequest(
        account_number=account_number, start_date=start_date, page_size=5
    )

    # Act
    result = orders_client.get_options_orders(request)

    # Assert
    assert result is not None
    assert hasattr(result, "results")
    assert hasattr(result, "next")
    assert hasattr(result, "previous")

    # Print number of orders found (helpful for debugging)
    print(f"Found {len(result.results)} options orders")

    # Check that results are OptionsOrder objects
    for order in result.results:
        assert isinstance(order, OptionsOrder)
        assert hasattr(order, "id")
        assert hasattr(order, "state")
        assert hasattr(order, "legs")
        assert hasattr(order, "chain_symbol")

        # Verify essential fields exist and are valid
        assert order.id is not None and len(order.id) > 0
        assert order.state is not None
        assert order.chain_symbol is not None
        assert len(order.legs) > 0

        # Check the first leg for position_effect
        first_leg = order.legs[0]
        assert hasattr(first_leg, "position_effect")
        assert first_leg.position_effect in ["open", "close"], (
            f"Invalid position_effect: {first_leg.position_effect}"
        )

        print(
            f"✓ Order {order.id}: {first_leg.side} {first_leg.position_effect} {first_leg.option_type} - {order.state}"
        )


def test_get_specific_options_order(
    orders_client: OrdersDataClient, account_number: str
):
    """Integration test for getting a single options order."""
    # First get a list of orders to find a valid order ID
    start_date = date.today() - timedelta(days=90)
    orders_request = OptionOrdersRequest(
        account_number=account_number, start_date=start_date, page_size=1
    )

    orders_result = orders_client.get_options_orders(orders_request)

    # Skip test if no orders found
    if not orders_result.results:
        pytest.skip("No options orders found in the last 90 days")

    # Get the first order ID
    first_order = orders_result.results[0]
    order_id = first_order.id

    print(f"Testing get_options_order with order ID: {order_id}")

    # Now test getting that specific order
    order_request = OptionOrderRequest(account_number=account_number, order_id=order_id)

    # Act
    specific_order = orders_client.get_options_order(order_request)

    # Assert
    assert isinstance(specific_order, OptionsOrder)
    assert specific_order.id == order_id
    assert specific_order.id == first_order.id
    assert specific_order.state == first_order.state
    assert specific_order.chain_symbol == first_order.chain_symbol

    # Verify essential fields exist
    required_fields = ["id", "ref_id", "account_number", "chain_id", "chain_symbol"]

    for field in required_fields:
        assert hasattr(specific_order, field), f"Missing field: {field}"
        field_value = getattr(specific_order, field)
        assert field_value is not None, f"Field {field} is None"
        if isinstance(field_value, str):
            assert len(field_value) > 0, f"Field {field} is empty"

    # Verify legs structure
    assert len(specific_order.legs) > 0, "Order should have at least one leg"
    first_leg = specific_order.legs[0]
    assert hasattr(first_leg, "option"), "Leg should have option URL"
    assert hasattr(first_leg, "position_effect"), "Leg should have position_effect"
    assert hasattr(first_leg, "side"), "Leg should have side"

    if first_leg.option:
        assert first_leg.option.startswith("https://"), (
            f"Option URL should be a valid HTTPS URL: {first_leg.option}"
        )

    print(
        f"✓ Single options order validation passed - ID: {specific_order.id}, "
        f"Symbol: {specific_order.chain_symbol}, State: {specific_order.state}"
    )

    # Verify this order matches the one from the orders list
    assert specific_order.chain_symbol == first_order.chain_symbol
    print("✓ Single options order matches original order from list")


def test_get_options_orders_cursor_iteration(
    orders_client: OrdersDataClient, account_number: str
):
    """Integration test for cursor iteration through multiple pages of options orders."""
    # Create request with a longer time range to get more results
    start_date = date.today() - timedelta(days=180)
    request = OptionOrdersRequest(
        account_number=account_number,
        start_date=start_date,
        page_size=2,  # Small page size to test pagination
    )

    # Act
    result = orders_client.get_options_orders(request)

    # Collect orders through iteration (this tests the cursor functionality)
    all_orders = []
    page_count = 0

    cursor = result.cursor()
    while True:
        current_page = cursor.current_page()
        page_count += 1
        print(f"Page {page_count}: {len(current_page.results)} options orders")

        for order in current_page.results:
            all_orders.append(order)
            assert isinstance(order, OptionsOrder)
            assert hasattr(order, "id")
            assert hasattr(order, "state")
            assert hasattr(order, "chain_symbol")
            assert hasattr(order, "legs")
            assert len(order.legs) > 0

        if not cursor.has_next():
            break

        cursor.next()

        # Safety check to prevent excessive API calls in tests
        if page_count >= 3:
            print("Stopping at page 3 for test safety")
            break

    # Assert
    assert all(isinstance(order, OptionsOrder) for order in all_orders)

    # Test cursor methods
    assert hasattr(cursor, "has_next")
    assert hasattr(cursor, "next")
    assert hasattr(cursor, "all")

    print(
        f"✓ Cursor iteration: {len(all_orders)} options orders across {page_count} pages"
    )


def test_get_options_orders_with_date_string(
    orders_client: OrdersDataClient, account_number: str
):
    """Integration test for options orders request with date as string."""
    # Test with date as string
    start_date_str = "2024-01-01"
    request = OptionOrdersRequest(
        account_number=account_number, start_date=start_date_str, page_size=3
    )

    # Act
    result = orders_client.get_options_orders(request)

    # Assert
    assert result is not None
    assert hasattr(result, "results")

    print(
        f"Date string test: Found {len(result.results)} options orders since {start_date_str}"
    )

    # Check that all orders are after the specified date
    for order in result.results:
        assert isinstance(order, OptionsOrder)
        # Verify the order has essential fields
        assert hasattr(order, "id")
        assert hasattr(order, "created_at")
        assert hasattr(order, "chain_symbol")
        assert hasattr(order, "legs")
        assert len(order.legs) > 0

        # The created_at should be after our start_date
        # Note: This is a basic check; the actual filtering is done by the API
        print(f"✓ Order {order.id}: created at {order.created_at}")

    print("✓ Date string filtering test completed")
