import unittest
from unittest.mock import patch

import robinhood_client as rh


class TestAuthentication(unittest.TestCase):
    """Test authentication functionality with mocked responses"""

    @patch('robinhood_client.authentication.request_post')
    def test_login_success(self, mock_post):
        # Arrange
        mock_response = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_in': 86400,
            'token_type': 'Bearer'
        }
        mock_post.return_value = mock_response

        # Act
        result = rh.login('test_user', 'test_password', store_session=False)

        # Assert
        self.assertTrue(result)
        mock_post.assert_called_once()


class TestStocks(unittest.TestCase):
    """Test stock-related functionality with mocked responses"""

    @patch('robinhood_client.stocks.request_get')
    def test_get_quotes(self, mock_get):
        # Arrange
        mock_response = [
            {
                'symbol': 'AAPL',
                'ask_price': '150.00',
                'bid_price': '149.50',
                'last_trade_price': '149.75',
                'previous_close': '148.50',
                'adjusted_previous_close': '148.50',
                'trading_halted': False,
                'has_traded': True,
                'last_trade_price_source': 'consolidated',
                'updated_at': '2023-01-01T12:00:00Z',
                'instrument': 'https://api.robinhood.com/instruments/450dfc6d-5510-4d40-abfb-f633b7d9be3e/'
            }
        ]
        mock_get.return_value = mock_response

        # Act
        result = rh.get_quotes('AAPL')

        # Assert
        self.assertEqual(result[0]['symbol'], 'AAPL')
        self.assertEqual(result[0]['ask_price'], '150.00')
        mock_get.assert_called_once()


if __name__ == '__main__':
    unittest.main()
