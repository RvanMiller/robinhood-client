"""Integration tests for the OrdersDataClient module."""

import os
import pytest
from datetime import datetime, timedelta

from robinhood_client.common.session import FileSystemSessionStorage
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import StockOrdersRequest


def test_get_stock_orders():
    """Integration test for getting stock orders."""
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
    
    # Login using the client's login method
    client.login(
        username=username, 
        password=password,
        mfa_code=mfa_code,
        persist_session=True
    )
    
    # Set account number from environment variable
    account_number = os.environ.get("RH_ACCOUNT_NUMBER")
    if not account_number:
        pytest.skip("RH_ACCOUNT_NUMBER environment variable is not set")
    
    # Create a request for recent orders (last 7 days)
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    request = StockOrdersRequest(
        account_number=account_number,
        start_date=one_week_ago,
        page_size=5
    )
    
    # Execute the request
    response = client.get_stock_orders(request)
    
    # Verify the response
    assert response is not None
    assert hasattr(response, "results")
    
    # Print number of orders found (helpful for debugging)
    print(f"Found {len(response.results)} orders")
    
    # If orders exist, verify basic structure of first order
    if response.results:
        first_order = response.results[0]
        assert hasattr(first_order, "id")
        assert hasattr(first_order, "instrument")
        assert hasattr(first_order, "quantity")
        assert hasattr(first_order, "price")
        assert hasattr(first_order, "side")
        assert hasattr(first_order, "status")
