"""Unit tests for the OptionsDataClient module."""

import unittest
from unittest.mock import patch, MagicMock

from robinhood_client.common.session import SessionStorage
from robinhood_client.common.schema import OptionsOrder
from robinhood_client.data.options import OptionsDataClient
from robinhood_client.data.requests import (
    OptionsOrderRequest,
)


class TestOptionsDataClient(unittest.TestCase):
    """Tests for the OptionsDataClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_storage = MagicMock(spec=SessionStorage)
        self.client = OptionsDataClient(session_storage=self.session_storage)

    def _create_complete_options_order_data(self, order_id, **overrides):
        """Helper method to create complete options order data for testing."""
        default_data = {
            "id": order_id,
            "ref_id": f"ref{order_id[5:]}",
            "account_number": "123ABC",
            "cancel_url": None,
            "canceled_quantity": "0.00000",
            "created_at": "2025-09-04T14:44:30.821142Z",
            "direction": "credit",
            "legs": [
                {
                    "id": "68b9a5ce-d3b4-4d85-a552-e436d2996a93",
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
                            "id": "68b9a5cf-ad88-4c27-96b1-a77a8d5b1b96",
                            "price": "1.51000000",
                            "quantity": "69.00000",
                            "settlement_date": "2025-09-05",
                            "timestamp": "2025-09-04T14:44:31.104000Z",
                        },
                        {
                            "id": "68b9a5cf-8c42-46ac-9ca5-edad7d07cc6a",
                            "price": "1.51000000",
                            "quantity": "1.00000",
                            "settlement_date": "2025-09-05",
                            "timestamp": "2025-09-04T14:44:31.104000Z",
                        },
                    ],
                }
            ],
            "pending_quantity": "0.00000",
            "premium": "151.00000000",
            "processed_premium": "11325",
            "processed_premium_direction": "credit",
            "net_amount": "11321.85",
            "net_amount_direction": "credit",
            "price": "1.51000000",
            "processed_quantity": "75.00000",
            "quantity": "75.00000",
            "regulatory_fees": "3.15",
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
            "estimated_total_net_amount": "11321.85",
            "estimated_total_net_amount_direction": "credit",
            "is_replaceable": False,
            "strategy": "short_call",
            "derived_state": "filled",
            "sales_taxes": [],
        }

        # Apply any overrides
        default_data.update(overrides)
        return default_data

    @patch.object(OptionsDataClient, "request_get")
    def test_get_options_order_success(self, mock_request_get):
        """Test successful retrieval of a single options order."""
        # Arrange
        order_id = "test-order-123"
        account_number = "123ABC"
        expected_data = self._create_complete_options_order_data(order_id)
        mock_request_get.return_value = expected_data

        request = OptionsOrderRequest(order_id=order_id, account_number=account_number)

        # Act
        result = self.client.get_options_order(request)

        # Assert
        self.assertIsInstance(result, OptionsOrder)
        self.assertEqual(result.id, order_id)
        self.assertEqual(result.state, "filled")  # enum as string
        self.assertEqual(result.chain_symbol, "AMZN")
        self.assertEqual(result.direction, "credit")
        self.assertEqual(len(result.legs), 1)

        # Check the first leg
        first_leg = result.legs[0]
        self.assertEqual(first_leg.position_effect, "close")
        self.assertEqual(first_leg.side, "sell")
        self.assertEqual(first_leg.option_type, "call")
        self.assertEqual(len(first_leg.executions), 2)

        mock_request_get.assert_called_once_with(
            f"/options/orders/{order_id}/", params={"account_number": account_number}
        )

    @patch.object(OptionsDataClient, "request_get")
    def test_get_options_order_without_account_number(self, mock_request_get):
        """Test retrieval of options order without account number parameter."""
        # Arrange
        order_id = "test-order-456"
        expected_data = self._create_complete_options_order_data(order_id)
        mock_request_get.return_value = expected_data

        request = OptionsOrderRequest(order_id=order_id)

        # Act
        result = self.client.get_options_order(request)

        # Assert
        self.assertIsInstance(result, OptionsOrder)
        self.assertEqual(result.id, order_id)

        mock_request_get.assert_called_once_with(
            f"/options/orders/{order_id}/", params={}
        )

    def test_get_options_order_with_position_effect_close(self):
        """Test options order with position_effect 'close'."""
        # Arrange
        order_id = "test-order-close"
        account_number = "123ABC"

        with patch.object(self.client, "request_get") as mock_request_get:
            expected_data = self._create_complete_options_order_data(
                order_id, direction="debit", closing_strategy="short_call"
            )
            # Update the leg to have position_effect "open" instead of "close"
            expected_data["legs"][0]["position_effect"] = "open"
            expected_data["legs"][0]["side"] = "buy"

            mock_request_get.return_value = expected_data

            request = OptionsOrderRequest(
                order_id=order_id, account_number=account_number
            )

            # Act
            result = self.client.get_options_order(request)

            # Assert
            self.assertEqual(result.direction, "debit")
            self.assertEqual(result.legs[0].position_effect, "open")
            self.assertEqual(result.legs[0].side, "buy")

    @patch.object(OptionsDataClient, "request_get")
    def test_get_options_order_handles_missing_optional_fields(self, mock_request_get):
        """Test that missing optional fields are handled properly."""
        # Arrange
        order_id = "test-order-minimal"
        minimal_data = self._create_complete_options_order_data(
            order_id,
            cancel_url=None,
            opening_strategy=None,
            closing_strategy=None,
            stop_price=None,
            response_category=None,
        )
        mock_request_get.return_value = minimal_data

        request = OptionsOrderRequest(order_id=order_id)

        # Act
        result = self.client.get_options_order(request)

        # Assert
        self.assertIsInstance(result, OptionsOrder)
        self.assertEqual(result.id, order_id)
        self.assertIsNone(result.cancel_url)
        self.assertIsNone(result.opening_strategy)
        self.assertIsNone(result.closing_strategy)
        self.assertIsNone(result.stop_price)
        self.assertIsNone(result.response_category)


if __name__ == "__main__":
    unittest.main()
