"""Unit tests for the OrdersDataClient module."""

import unittest
from unittest.mock import patch, MagicMock

from robinhood_client.common.session import SessionStorage
from robinhood_client.common.schema import StockOrder
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import (
    StockOrderRequest,
)


class TestOrdersDataClient(unittest.TestCase):
    """Tests for the OrdersDataClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_storage = MagicMock(spec=SessionStorage)
        self.client = OrdersDataClient(session_storage=self.session_storage)

    def _create_complete_order_data(self, order_id, **overrides):
        """Helper method to create complete order data for testing."""
        default_data = {
            "id": order_id,
            "ref_id": f"ref{order_id[5:]}",  # Extract number from "orderXXX"
            "url": f"http://example.com/orders/{order_id}/",
            "account": f"http://example.com/accounts/account{order_id[5:]}/",
            "user_uuid": f"user-uuid-{order_id[5:]}",
            "position": f"http://example.com/positions/position{order_id[5:]}/",
            "cancel": None,
            "instrument": "http://example.com/instruments/AAPL/",
            "instrument_id": f"instrument-id-{order_id[5:]}",
            "cumulative_quantity": "0.00000000",
            "average_price": None,
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
            "quantity": "10.00000000",
            "reject_reason": None,
            "created_at": "2025-01-01T12:00:00.000000Z",
            "updated_at": "2025-01-01T12:05:00.000000Z",
            "last_transaction_at": "2025-01-01T12:05:00.000000Z",
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
            "last_update_version": 1,
            "placed_agent": "user",
            "is_editable": False,
            "replaces": None,
            "user_cancel_request_state": "order_finalized",
            "tax_lot_selection_type": None,
            "position_effect": "open",
        }

        # Apply any overrides
        default_data.update(overrides)
        return default_data

    def test_init(self):
        """Test the initialization of OrdersDataClient."""
        self.assertEqual(self.client._session_storage, self.session_storage)

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_order_with_account_number(self, mock_request_get):
        """Test getting a specific stock order with account number."""
        # Arrange
        mock_request_get.return_value = self._create_complete_order_data("order123")

        request = StockOrderRequest(account_number="account123", order_id="order123")

        # Act
        response = self.client.get_stock_order(request)

        # Assert
        self.assertIsInstance(response, StockOrder)
        self.assertEqual(response.id, "order123")
        self.assertEqual(response.quantity, "10.00000000")
        self.assertEqual(response.side, "buy")  # enum as string
        self.assertEqual(response.state, "filled")  # enum as string

        mock_request_get.assert_called_once_with(
            "/orders/order123/", params={"account_number": "account123"}
        )

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_order_without_account_number(self, mock_request_get):
        """Test getting a specific stock order without account number."""
        # Arrange
        mock_request_get.return_value = self._create_complete_order_data(
            "order456",
            instrument="http://example.com/instruments/MSFT/",
            instrument_id="instrument-id-456",
            cumulative_quantity="5.00000000",
            average_price="300.00",
            state="cancelled",
            derived_state="cancelled",
            type="limit",
            side="sell",
            price="300.00",
            quantity="5.00000000",
            created_at="2025-02-01T12:00:00.000000Z",
            updated_at="2025-02-01T12:05:00.000000Z",
            last_transaction_at="2025-02-01T12:05:00.000000Z",
            order_form_type="share_based_limit_sells",
            position_effect="close",
        )

        request = StockOrderRequest(order_id="order456")

        # Act
        response = self.client.get_stock_order(request)

        # Assert
        self.assertIsInstance(response, StockOrder)
        self.assertEqual(response.id, "order456")
        self.assertEqual(response.quantity, "5.00000000")
        self.assertEqual(response.price, "300.00")
        self.assertEqual(response.side, "sell")
        self.assertEqual(response.state, "cancelled")

        mock_request_get.assert_called_once_with("/orders/order456/", params={})

    def test_default_session_storage(self):
        """Test OrdersDataClient uses FileSystemSessionStorage by default."""
        from robinhood_client.common.session import FileSystemSessionStorage

        client = OrdersDataClient()
        self.assertIsInstance(client._session_storage, FileSystemSessionStorage)

    @patch("robinhood_client.data.orders.ApiCursor")
    def test_get_stock_orders_filters(self, mock_api_cursor):
        """Test get_stock_orders applies state, start_date, and end_date filters."""
        mock_cursor_instance = MagicMock()
        mock_api_cursor.return_value = mock_cursor_instance
        from robinhood_client.data.requests import StockOrdersRequest
        import datetime

        request = StockOrdersRequest(
            account_number="acc123",
            page_size=5,
            state="filled",
            start_date=datetime.date(2025, 1, 1),
            end_date=datetime.date(2025, 1, 31),
        )
        client = OrdersDataClient(
            session_storage=self.session_storage, resolve_symbols=False
        )
        result = client.get_stock_orders(request)
        # Assert correct parameters passed to ApiCursor
        called_args = mock_api_cursor.call_args[1]["base_params"]
        self.assertEqual(called_args["state"], "filled")
        self.assertEqual(called_args["updated_at[gte]"], "2025-01-01")
        self.assertEqual(called_args["updated_at[lte]"], "2025-01-31")
        # Assert result is a PaginatedResult
        from robinhood_client.common.cursor import PaginatedResult

        self.assertIsInstance(result, PaginatedResult)

    @patch("robinhood_client.data.orders.ApiCursor")
    def test_get_options_orders_filters(self, mock_api_cursor):
        """Test get_options_orders applies state, start_date, and end_date filters."""
        mock_cursor_instance = MagicMock()
        mock_api_cursor.return_value = mock_cursor_instance
        from robinhood_client.data.requests import OptionOrdersRequest
        import datetime

        request = OptionOrdersRequest(
            account_number="acc456",
            page_size=10,
            state="cancelled",
            start_date=datetime.date(2025, 2, 1),
            end_date=datetime.date(2025, 2, 28),
        )
        client = OrdersDataClient(session_storage=self.session_storage)
        result = client.get_options_orders(request)
        self.assertIs(result.cursor(), mock_cursor_instance)
        called_args = mock_api_cursor.call_args[1]["base_params"]
        self.assertEqual(called_args["state"], "cancelled")
        self.assertEqual(called_args["updated_at[gte]"], "2025-02-01")
        self.assertEqual(called_args["updated_at[lte]"], "2025-02-28")


if __name__ == "__main__":
    unittest.main()
