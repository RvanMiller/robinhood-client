"""Unit tests for the OrdersDataClient module."""

import unittest
from unittest.mock import patch, MagicMock

from robinhood_client.common.session import SessionStorage
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import (
    StockOrderRequest,
    StockOrderResponse,
    StockOrdersRequest,
    StockOrdersResponse,
)


class TestOrdersDataClient(unittest.TestCase):
    """Tests for the OrdersDataClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_storage = MagicMock(spec=SessionStorage)
        self.client = OrdersDataClient(session_storage=self.session_storage)

    def test_init(self):
        """Test the initialization of OrdersDataClient."""
        self.assertEqual(self.client._session_storage, self.session_storage)

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_order_with_account_number(self, mock_request_get):
        """Test getting a specific stock order with account number."""
        # Arrange
        mock_request_get.return_value = {
            "id": "order123",
            "instrument": {
                "symbol": "AAPL",
                "url": "http://example.com/instruments/AAPL/",
            },
            "quantity": 10,
            "price": 150.0,
            "side": "buy",
            "status": "filled",
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:05:00Z",
        }

        request = StockOrderRequest(account_number="account123", order_id="order123")

        # Act
        response = self.client.get_stock_order(request)

        # Assert
        self.assertIsInstance(response, StockOrderResponse)
        self.assertEqual(response.id, "order123")
        self.assertEqual(response.quantity, 10)
        self.assertEqual(response.price, 150.0)
        self.assertEqual(response.side, "buy")
        self.assertEqual(response.status, "filled")

        mock_request_get.assert_called_once_with(
            "/orders/order123/", params={"account_number": "account123"}
        )

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_order_without_account_number(self, mock_request_get):
        """Test getting a specific stock order without account number."""
        # Arrange
        mock_request_get.return_value = {
            "id": "order456",
            "instrument": {
                "symbol": "MSFT",
                "url": "http://example.com/instruments/MSFT/",
            },
            "quantity": 5,
            "price": 300.0,
            "side": "sell",
            "status": "pending",
            "created_at": "2025-02-01T12:00:00Z",
            "updated_at": "2025-02-01T12:05:00Z",
        }

        request = StockOrderRequest(order_id="order456")

        # Act
        response = self.client.get_stock_order(request)

        # Assert
        self.assertIsInstance(response, StockOrderResponse)
        self.assertEqual(response.id, "order456")
        self.assertEqual(response.quantity, 5)
        self.assertEqual(response.price, 300.0)
        self.assertEqual(response.side, "sell")
        self.assertEqual(response.status, "pending")

        mock_request_get.assert_called_once_with("/orders/order456/", params={})

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_orders_with_all_params(self, mock_request_get):
        """Test getting all stock orders with all parameters."""
        # Arrange
        mock_request_get.return_value = {
            "results": [
                {
                    "id": "order123",
                    "instrument": {
                        "symbol": "AAPL",
                        "url": "http://example.com/instruments/AAPL/",
                    },
                    "quantity": 10,
                    "price": 150.0,
                    "side": "buy",
                    "status": "filled",
                    "created_at": "2025-01-01T12:00:00Z",
                    "updated_at": "2025-01-01T12:05:00Z",
                },
                {
                    "id": "order456",
                    "instrument": {
                        "symbol": "MSFT",
                        "url": "http://example.com/instruments/MSFT/",
                    },
                    "quantity": 5,
                    "price": 300.0,
                    "side": "sell",
                    "status": "pending",
                    "created_at": "2025-02-01T12:00:00Z",
                    "updated_at": "2025-02-01T12:05:00Z",
                },
            ],
            "next": "http://example.com/orders/?cursor=next_page",
            "previous": None,
        }

        request = StockOrdersRequest(
            account_number="account123", start_date="2025-01-01", page_size=25
        )

        # Act
        response = self.client.get_stock_orders(request)

        # Assert
        self.assertIsInstance(response, StockOrdersResponse)
        self.assertEqual(len(response.results), 2)
        self.assertEqual(response.results[0].id, "order123")
        self.assertEqual(response.results[0].quantity, 10)
        self.assertEqual(response.results[1].id, "order456")
        self.assertEqual(response.results[1].side, "sell")
        self.assertEqual(response.next, "http://example.com/orders/?cursor=next_page")
        self.assertIsNone(response.previous)

        mock_request_get.assert_called_once_with(
            "/orders/",
            params={
                "account_number": "account123",
                "start_date": "2025-01-01",
                "page_size": 25,
            },
        )

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_orders_with_only_account_number(self, mock_request_get):
        """Test getting all stock orders with only account number."""
        # Arrange
        mock_request_get.return_value = {
            "results": [
                {
                    "id": "order789",
                    "instrument": {
                        "symbol": "GOOGL",
                        "url": "http://example.com/instruments/GOOGL/",
                    },
                    "quantity": 2,
                    "price": 1500.0,
                    "side": "buy",
                    "status": "filled",
                    "created_at": "2025-03-01T12:00:00Z",
                    "updated_at": "2025-03-01T12:05:00Z",
                }
            ],
            "next": None,
            "previous": None,
        }

        request = StockOrdersRequest(account_number="account789")

        # Act
        response = self.client.get_stock_orders(request)

        # Assert
        self.assertIsInstance(response, StockOrdersResponse)
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].id, "order789")
        self.assertEqual(response.results[0].price, 1500.0)
        self.assertIsNone(response.next)
        self.assertIsNone(response.previous)

        mock_request_get.assert_called_once_with(
            "/orders/", params={"account_number": "account789", "page_size": 10}
        )

    @patch.object(OrdersDataClient, "request_get")
    def test_get_stock_orders_empty_response(self, mock_request_get):
        """Test getting stock orders with an empty response."""
        # Arrange
        mock_request_get.return_value = {"results": [], "next": None, "previous": None}

        request = StockOrdersRequest(account_number="empty_account")

        # Act
        response = self.client.get_stock_orders(request)

        # Assert
        self.assertIsInstance(response, StockOrdersResponse)
        self.assertEqual(len(response.results), 0)
        self.assertIsNone(response.next)
        self.assertIsNone(response.previous)

        mock_request_get.assert_called_once_with(
            "/orders/", params={"account_number": "empty_account", "page_size": 10}
        )


if __name__ == "__main__":
    unittest.main()
