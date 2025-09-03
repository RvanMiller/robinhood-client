"""Unit tests for OrdersDataClient cursor integration."""

from unittest.mock import Mock, patch
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import StockOrdersRequest
from robinhood_client.common.cursor import PaginatedResult
from robinhood_client.common.schema import StockOrder


class TestOrdersDataClientCursor:
    """Test cursor integration in OrdersDataClient."""

    def create_mock_stock_order_data(self, order_id: str) -> dict:
        """Create a mock stock order data dictionary."""
        return {
            "id": order_id,
            "ref_id": f"ref_{order_id}",
            "url": f"https://api.robinhood.com/orders/{order_id}/",
            "account": "https://api.robinhood.com/accounts/123/",
            "user_uuid": "user-uuid",
            "position": f"https://api.robinhood.com/positions/123/{order_id}/",
            "cancel": None,
            "instrument": "https://api.robinhood.com/instruments/abc123/",
            "instrument_id": "abc123",
            "cumulative_quantity": "10.0000",
            "average_price": "150.00",
            "fees": "0.00",
            "sec_fees": "0.00",
            "taf_fees": "0.00",
            "cat_fees": "0.00",
            "sales_taxes": [],
            "state": "filled",
            "derived_state": "filled",
            "pending_cancel_open_agent": None,
            "type": "market",
            "side": "buy",
            "time_in_force": "gfd",
            "trigger": "immediate",
            "price": None,
            "stop_price": None,
            "quantity": "10.0000",
            "reject_reason": None,
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-01T10:00:00Z",
            "last_transaction_at": "2023-01-01T10:00:00Z",
            "executions": [],
            "extended_hours": False,
            "market_hours": "regular_hours",
            "override_dtbp_checks": False,
            "override_day_trade_checks": False,
            "response_category": None,
            "stop_triggered_at": None,
            "last_trail_price": None,
            "last_trail_price_updated_at": None,
            "last_trail_price_source": None,
            "dollar_based_amount": None,
            "total_notional": None,
            "executed_notional": None,
            "investment_schedule_id": None,
            "is_ipo_access_order": False,
            "ipo_access_cancellation_reason": None,
            "ipo_access_lower_collared_price": None,
            "ipo_access_upper_collared_price": None,
            "ipo_access_upper_price": None,
            "ipo_access_lower_price": None,
            "is_ipo_access_price_finalized": False,
            "is_visible_to_user": True,
            "has_ipo_access_custom_price_limit": False,
            "is_primary_account": True,
            "order_form_version": 6,
            "preset_percent_limit": None,
            "order_form_type": "share_based_market_buys",
            "last_update_version": 2,
            "placed_agent": "user",
            "is_editable": False,
            "replaces": None,
            "user_cancel_request_state": "order_finalized",
            "tax_lot_selection_type": None,
            "position_effect": "open",
        }

    @patch("robinhood_client.data.orders.OrdersDataClient.__init__", return_value=None)
    def test_get_stock_orders_returns_paginated_result(self, mock_init):
        """Test that get_stock_orders returns a PaginatedResult."""
        # Setup
        client = OrdersDataClient.__new__(OrdersDataClient)

        # Mock the request_get method to return mock data
        mock_response = {
            "results": [self.create_mock_stock_order_data("order1")],
            "next": "https://api.robinhood.com/orders/?cursor=next",
            "previous": None,
            "count": 1,
        }
        client.request_get = Mock(return_value=mock_response)

        request = StockOrdersRequest(account_number="123456", page_size=10)

        # Execute
        result = client.get_stock_orders(request)

        # Verify
        assert isinstance(result, PaginatedResult)
        assert len(result.results) == 1
        assert isinstance(result.results[0], StockOrder)
        assert result.results[0].id == "order1"
        assert result.next == "https://api.robinhood.com/orders/?cursor=next"

    @patch("robinhood_client.data.orders.OrdersDataClient.__init__", return_value=None)
    def test_cursor_iteration_across_pages(self, mock_init):
        """Test that cursor can iterate across multiple pages."""
        # Setup
        client = OrdersDataClient.__new__(OrdersDataClient)

        # Mock responses for pagination
        page1_response = {
            "results": [self.create_mock_stock_order_data("order1")],
            "next": "https://api.robinhood.com/orders/?cursor=page2",
            "previous": None,
            "count": 2,
        }

        page2_response = {
            "results": [self.create_mock_stock_order_data("order2")],
            "next": None,
            "previous": "https://api.robinhood.com/orders/?cursor=page1",
            "count": 2,
        }

        client.request_get = Mock(side_effect=[page1_response, page2_response])

        request = StockOrdersRequest(account_number="123456", page_size=1)
        result = client.get_stock_orders(request)

        # Execute - iterate through all pages
        all_orders = list(result)

        # Verify
        assert len(all_orders) == 2
        assert all_orders[0].id == "order1"
        assert all_orders[1].id == "order2"
        assert client.request_get.call_count == 2

    @patch("robinhood_client.data.orders.OrdersDataClient.__init__", return_value=None)
    def test_cursor_manual_pagination(self, mock_init):
        """Test manual pagination with cursor methods."""
        # Setup
        client = OrdersDataClient.__new__(OrdersDataClient)

        page1_response = {
            "results": [self.create_mock_stock_order_data("order1")],
            "next": "https://api.robinhood.com/orders/?cursor=page2",
            "previous": None,
            "count": 2,
        }

        page2_response = {
            "results": [self.create_mock_stock_order_data("order2")],
            "next": None,
            "previous": "https://api.robinhood.com/orders/?cursor=page1",
            "count": 2,
        }

        client.request_get = Mock(side_effect=[page1_response, page2_response])

        request = StockOrdersRequest(account_number="123456", page_size=1)
        result = client.get_stock_orders(request)

        # Execute manual pagination
        cursor = result.cursor()

        # Check first page
        first_page = cursor.current_page()
        assert len(first_page.results) == 1
        assert first_page.results[0].id == "order1"
        assert cursor.has_next()

        # Move to next page
        second_page = cursor.next()
        assert len(second_page.results) == 1
        assert second_page.results[0].id == "order2"
        assert not cursor.has_next()
        assert cursor.has_previous()

    @patch("robinhood_client.data.orders.OrdersDataClient.__init__", return_value=None)
    def test_get_stock_orders_returns_cursor_result(self, mock_init):
        """Test that the get_stock_orders method returns a PaginatedResult."""
        # Setup
        client = OrdersDataClient.__new__(OrdersDataClient)

        mock_response = {
            "results": [self.create_mock_stock_order_data("order1")],
            "next": "https://api.robinhood.com/orders/?cursor=next",
            "previous": None,
        }
        client.request_get = Mock(return_value=mock_response)

        request = StockOrdersRequest(account_number="123456", page_size=10)

        # Execute method
        result = client.get_stock_orders(request)

        # Verify it returns a PaginatedResult
        assert isinstance(result, PaginatedResult)
        assert len(result.results) == 1
        assert isinstance(result.results[0], StockOrder)
        assert result.next == "https://api.robinhood.com/orders/?cursor=next"
