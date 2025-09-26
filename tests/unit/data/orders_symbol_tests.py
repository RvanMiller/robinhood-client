"""Unit tests for symbol resolution in orders client."""

from unittest.mock import Mock, patch
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import StockOrderRequest, StockOrdersRequest
from robinhood_client.common.session import SessionStorage


class TestOrdersDataClientSymbolResolution:
    """Test cases for symbol resolution in OrdersDataClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session_storage = Mock(spec=SessionStorage)
        self.client = OrdersDataClient(self.mock_session_storage)

    def create_mock_order_response(
        self, order_id: str = "test-order-id", account_number: str = "test-account"
    ) -> dict:
        """Create a mock stock order response."""
        return {
            "id": order_id,
            "ref_id": "ref123",
            "url": f"https://api.robinhood.com/orders/{order_id}/",
            "account": f"https://api.robinhood.com/accounts/{account_number}/",
            "user_uuid": "user-uuid",
            "position": "https://api.robinhood.com/positions/pos123/",
            "cancel": None,
            "instrument": "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/",
            "instrument_id": "e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6",
            "cumulative_quantity": "0.00000000",
            "average_price": None,
            "fees": "0.00",
            "sec_fees": "0.00",
            "taf_fees": "0.00",
            "cat_fees": "0.00",
            "sales_taxes": [],
            "state": "cancelled",
            "derived_state": "cancelled",
            "pending_cancel_open_agent": None,
            "type": "market",
            "side": "buy",
            "time_in_force": "gfd",
            "trigger": "immediate",
            "price": None,
            "stop_price": None,
            "quantity": "1.00000000",
            "reject_reason": None,
            "created_at": "2023-01-01T00:00:00.000000Z",
            "updated_at": "2023-01-01T00:05:00.000000Z",
            "last_transaction_at": "2023-01-01T00:05:00.000000Z",
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
            "position_effect": None,
        }

    def test_get_stock_order_with_symbol_resolution_enabled(self):
        """Test getting a single stock order with symbol resolution enabled."""
        order_id = "test-order-id"
        account_number = "test-account"

        mock_order_response = self.create_mock_order_response(order_id, account_number)

        with (
            patch.object(self.client, "request_get") as mock_request_get,
            patch.object(
                self.client._instrument_client, "get_symbol_by_instrument_url"
            ) as mock_get_symbol,
        ):
            mock_request_get.return_value = mock_order_response
            mock_get_symbol.return_value = "CRDO"

            # Create request with symbol resolution enabled
            request = StockOrderRequest(
                account_number=account_number, order_id=order_id, resolve_symbols=True
            )

            # Get the order
            order = self.client.get_stock_order(request)

            # Verify API call
            mock_request_get.assert_called_once_with(
                f"/orders/{order_id}/", params={"account_number": account_number}
            )

            # Verify symbol resolution was called
            mock_get_symbol.assert_called_once_with(
                "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
            )

            # Verify order properties
            assert order.id == order_id
            assert order.symbol == "CRDO"  # Symbol should be resolved
            assert (
                order.instrument
                == "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
            )

    def test_get_stock_order_with_symbol_resolution_disabled(self):
        """Test getting a single stock order with symbol resolution disabled."""
        order_id = "test-order-id"
        account_number = "test-account"

        mock_order_response = self.create_mock_order_response(order_id, account_number)

        with (
            patch.object(self.client, "request_get") as mock_request_get,
            patch.object(
                self.client._instrument_client, "get_symbol_by_instrument_url"
            ) as mock_get_symbol,
        ):
            mock_request_get.return_value = mock_order_response

            # Create request with symbol resolution disabled
            request = StockOrderRequest(
                account_number=account_number, order_id=order_id, resolve_symbols=False
            )

            # Get the order
            order = self.client.get_stock_order(request)

            # Verify API call
            mock_request_get.assert_called_once_with(
                f"/orders/{order_id}/", params={"account_number": account_number}
            )

            # Verify symbol resolution was NOT called
            mock_get_symbol.assert_not_called()

            # Verify order properties
            assert order.id == order_id
            assert order.symbol is None  # Symbol should not be resolved
            assert (
                order.instrument
                == "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
            )

    def test_request_defaults(self):
        """Test that resolve_symbols defaults to True in request models."""
        # Test StockOrderRequest
        request = StockOrderRequest(order_id="test-id")
        assert request.resolve_symbols is True

        # Test StockOrdersRequest
        request = StockOrdersRequest(account_number="test-account")
        assert request.resolve_symbols is True
