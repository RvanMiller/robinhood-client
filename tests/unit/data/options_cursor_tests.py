"""Unit tests for OrdersDataClient options cursor integration."""

from unittest.mock import Mock, patch
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import OptionOrdersRequest
from robinhood_client.common.cursor import PaginatedResult
from robinhood_client.common.schema import OptionsOrder


class TestOrdersDataClientOptionsCursor:
    """Test cursor integration in OrdersDataClient for options orders."""

    def create_mock_options_order_data(self, order_id: str) -> dict:
        """Create a mock options order data dictionary."""
        return {
            "id": order_id,
            "ref_id": f"ref_{order_id}",
            "account_number": "123ABC",
            "cancel_url": None,
            "canceled_quantity": "0.00000",
            "created_at": "2025-09-04T14:44:30.821142Z",
            "direction": "credit",
            "legs": [
                {
                    "id": f"leg_{order_id}",
                    "option": "https://api.robinhood.com/options/instruments/fd9c5d5b-b158-4edb-9c7a-4d8c4699c9fb/",
                    "position_effect": "close",
                    "ratio_quantity": 1,
                    "side": "sell",
                    "expiration_date": "2025-10-17",
                    "strike_price": "255.0000",
                    "option_type": "call",
                    "long_strategy_code": "fd9c5d5b-b158-4edb-9c7a-4d8c4699c9fb_L1",
                    "short_strategy_code": "fd9c5d5b-b158-4edb-9c7a-4d8c4699c9fb_S1",
                    "executions": [
                        {
                            "id": f"execution_{order_id}",
                            "price": "1.51000000",
                            "quantity": "10.00000",
                            "settlement_date": "2025-09-05",
                            "timestamp": "2025-09-04T14:44:31.104000Z",
                        }
                    ],
                }
            ],
            "pending_quantity": "0.00000",
            "premium": "151.00000000",
            "processed_premium": "1510",
            "processed_premium_direction": "credit",
            "net_amount": "1500.00",
            "net_amount_direction": "credit",
            "price": "1.51000000",
            "processed_quantity": "10.00000",
            "quantity": "10.00000",
            "regulatory_fees": "0.15",
            "contract_fees": "0",
            "gold_savings": "0",
            "state": "filled",
            "time_in_force": "gfd",
            "trigger": "immediate",
            "type": "limit",
            "updated_at": "2025-09-04T14:44:32.121636Z",
            "chain_id": "b82496ae-28c7-4837-a0a5-33b73e93aca8",
            "chain_symbol": "AMZN",
            "response_category": None,
            "opening_strategy": None,
            "closing_strategy": "long_call",
            "stop_price": None,
            "form_source": "order_form_flyover",
            "client_bid_at_submission": "1.51000000",
            "client_ask_at_submission": "1.54000000",
            "client_time_at_submission": None,
            "average_net_premium_paid": "-151.00000000",
            "estimated_total_net_amount": "1500.00",
            "estimated_total_net_amount_direction": "credit",
            "is_replaceable": False,
            "strategy": "short_call",
            "derived_state": "filled",
            "sales_taxes": [],
        }

    def test_get_options_orders_returns_paginated_result(self):
        """Test that get_options_orders returns a PaginatedResult."""
        # Setup - use a mock session storage instead of bypassing __init__
        mock_session_storage = Mock()
        client = OrdersDataClient(session_storage=mock_session_storage)

        # Mock the first page response
        mock_first_page = {
            "results": [
                self.create_mock_options_order_data("order1"),
                self.create_mock_options_order_data("order2"),
            ],
            "next": "https://api.robinhood.com/options/orders/?cursor=next_page",
            "previous": None,
            "count": 10,
        }

        # Mock the request_get method directly
        with patch.object(client, "request_get", return_value=mock_first_page):
            request = OptionOrdersRequest(account_number="123")

            # Act
            result = client.get_options_orders(request)

            # Access results to trigger the actual request
            actual_results = result.results

            # Assert
            assert isinstance(result, PaginatedResult)
            assert len(actual_results) == 2
            assert all(isinstance(order, OptionsOrder) for order in actual_results)
            assert result.next is not None
            assert result.previous is None

    def test_cursor_iteration_through_multiple_pages(self):
        """Test cursor iteration through multiple pages of options orders."""
        # Setup
        mock_session_storage = Mock()
        client = OrdersDataClient(session_storage=mock_session_storage)

        # Mock responses for multiple pages
        mock_responses = [
            # First page
            {
                "results": [
                    self.create_mock_options_order_data("order1"),
                    self.create_mock_options_order_data("order2"),
                ],
                "next": "https://api.robinhood.com/options/orders/?cursor=page2",
                "previous": None,
                "count": 4,
            },
            # Second page
            {
                "results": [
                    self.create_mock_options_order_data("order3"),
                    self.create_mock_options_order_data("order4"),
                ],
                "next": None,
                "previous": "https://api.robinhood.com/options/orders/?cursor=page1",
                "count": 4,
            },
        ]

        with patch.object(client, "request_get", side_effect=mock_responses):
            request = OptionOrdersRequest(account_number="123", page_size=2)
            result = client.get_options_orders(request)

            # Act - iterate through all orders
            all_orders = list(result)

            # Assert
            assert len(all_orders) == 4
            order_ids = [order.id for order in all_orders]
            assert order_ids == ["order1", "order2", "order3", "order4"]

    def test_cursor_all_method_collects_all_orders(self):
        """Test that cursor.all() method collects all orders from all pages."""
        # Setup

        mock_session_storage = Mock()
        client = OrdersDataClient(session_storage=mock_session_storage)

        mock_responses = [
            # First page
            {
                "results": [
                    self.create_mock_options_order_data("order1"),
                    self.create_mock_options_order_data("order2"),
                ],
                "next": "https://api.robinhood.com/options/orders/?cursor=page2",
                "previous": None,
                "count": 3,
            },
            # Second page (last page)
            {
                "results": [self.create_mock_options_order_data("order3")],
                "next": None,
                "previous": "https://api.robinhood.com/options/orders/?cursor=page1",
                "count": 3,
            },
        ]

        with patch.object(client, "request_get", side_effect=mock_responses):
            request = OptionOrdersRequest(account_number="123")
            result = client.get_options_orders(request)

            # Act
            all_orders = result.cursor().all()

            # Assert
            assert len(all_orders) == 3
            order_ids = [order.id for order in all_orders]
            assert order_ids == ["order1", "order2", "order3"]

    def test_get_options_orders_with_date_filter(self):
        """Test get_options_orders with start_date parameter."""
        # Setup

        mock_session_storage = Mock()
        client = OrdersDataClient(session_storage=mock_session_storage)

        mock_response = {
            "results": [self.create_mock_options_order_data("order1")],
            "next": None,
            "previous": None,
            "count": 1,
        }

        with patch.object(
            client, "request_get", return_value=mock_response
        ) as mock_get:
            request = OptionOrdersRequest(
                account_number="123", start_date="2023-01-01", page_size=5
            )

            # Act
            result = client.get_options_orders(request)

            # Assert - access results to trigger the request
            _ = result.results

            mock_get.assert_called_once()
            call_args = mock_get.call_args

            # Check the endpoint
            assert call_args[0][0] == "/options/orders/"

            # Check the parameters
            params = call_args[1]["params"]
            assert params["account_number"] == "123"
            assert params["updated_at[gte]"] == "2023-01-01"
            assert params["page_size"] == 5

    def test_get_options_orders_default_page_size(self):
        """Test that default page_size is applied when not specified."""
        # Setup

        mock_session_storage = Mock()
        client = OrdersDataClient(session_storage=mock_session_storage)

        mock_response = {"results": [], "next": None, "previous": None, "count": 0}

        with patch.object(
            client, "request_get", return_value=mock_response
        ) as mock_get:
            request = OptionOrdersRequest(account_number="123")

            # Act
            result = client.get_options_orders(request)

            # Access results to trigger the request
            _ = result.results

            # Assert
            params = mock_get.call_args[1]["params"]
            assert params["page_size"] == 10  # Default page size

    def test_cursor_has_next_functionality(self):
        """Test cursor has_next() method functionality."""
        # Setup

        mock_session_storage = Mock()
        client = OrdersDataClient(session_storage=mock_session_storage)

        mock_response_with_next = {
            "results": [self.create_mock_options_order_data("order1")],
            "next": "https://api.robinhood.com/options/orders/?cursor=page2",
            "previous": None,
            "count": 2,
        }

        with patch.object(client, "request_get", return_value=mock_response_with_next):
            request = OptionOrdersRequest(account_number="123")
            result = client.get_options_orders(request)

            # Act & Assert
            cursor = result.cursor()
            assert cursor.has_next() is True

        # Test with no next page
        mock_response_no_next = {
            "results": [self.create_mock_options_order_data("order1")],
            "next": None,
            "previous": None,
            "count": 1,
        }

        with patch.object(client, "request_get", return_value=mock_response_no_next):
            request = OptionOrdersRequest(account_number="123")
            result = client.get_options_orders(request)

            # Act & Assert
            cursor = result.cursor()
            assert cursor.has_next() is False
