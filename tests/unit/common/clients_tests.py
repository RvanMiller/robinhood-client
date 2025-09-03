"""Unit tests for the clients module."""

import unittest
import requests
from unittest.mock import patch, MagicMock


from robinhood_client.common.clients import BaseClient, BaseOAuthClient
from robinhood_client.common.session import SessionStorage
from robinhood_client.common.exceptions import AuthenticationError
from robinhood_client.common.constants import BASE_API_URL, API_LOGIN_URL


class TestBaseClient(unittest.TestCase):
    """Tests for the BaseClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = BaseClient()

    def test_init(self):
        """Test the initialization of BaseClient."""
        self.assertIsInstance(self.client._session, requests.Session)
        self.assertEqual(
            self.client._session.headers["X-Robinhood-API-Version"], "1.431.4"
        )
        self.assertEqual(
            self.client._session.headers["Content-Type"],
            "application/x-www-form-urlencoded; charset=utf-8",
        )

    @patch("requests.Session.get")
    def test_request_get_success(self, mock_get):
        """Test successful GET request."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        # Act
        result = self.client.request_get("http://example.com")

        # Assert
        self.assertEqual(result, {"key": "value"})
        mock_get.assert_called_once_with("http://example.com", params=None)

    @patch("requests.Session.get")
    def test_request_get_with_params(self, mock_get):
        """Test GET request with parameters."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        # Act
        result = self.client.request_get("http://example.com", {"param": "value"})

        # Assert
        self.assertEqual(result, {"results": []})
        mock_get.assert_called_once_with(
            "http://example.com", params={"param": "value"}
        )

    @patch("requests.Session.get")
    def test_request_get_error(self, mock_get):
        """Test GET request with an error."""
        # Arrange
        mock_get.side_effect = Exception("Connection error")

        # Act
        with self.assertLogs(level="ERROR") as log:
            self.client.request_get("http://example.com")

        # Assert
        self.assertIn(
            "ERROR:robinhood_client.common.clients:Error in BaseClient request_get",
            log.output[0],
        )

    @patch("requests.Session.post")
    def test_request_post_success(self, mock_post):
        """Test successful POST request."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"token": "abc123"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Act
        result = self.client.request_post("http://example.com", {"user": "name"})

        # Assert
        self.assertEqual(result, {"token": "abc123"})
        mock_post.assert_called_once_with(
            "http://example.com", data={"user": "name"}, timeout=16
        )

    @patch("requests.Session.post")
    def test_request_post_json_request(self, mock_post):
        """Test POST request with JSON payload."""
        # Arrange
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Act
        result = self.client.request_post(
            "http://example.com", {"data": "json"}, json_request=True
        )

        # Assert
        self.assertEqual(result, {"result": "success"})
        mock_post.assert_called_once_with(
            "http://example.com", json={"data": "json"}, timeout=16
        )

    @patch("requests.Session.post")
    def test_request_post_non_json_response(self, mock_post):
        """Test POST request with non-JSON response."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # Act
        result = self.client.request_post(
            "http://example.com", {"data": "form"}, json_response=False
        )

        # Assert
        self.assertEqual(result, mock_response)
        mock_post.assert_called_once_with(
            "http://example.com", data={"data": "form"}, timeout=16
        )

    @patch("requests.Session.post")
    def test_request_post_error_status_code(self, mock_post):
        """Test POST request with error status code."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # Act
        with self.assertLogs(level="ERROR") as log:
            self.client.request_post("http://example.com")

        # Assert
        self.assertIn(
            "ERROR:robinhood_client.common.clients:Error in BaseClient request_post",
            log.output[0],
        )


class TestBaseOAuthClient(unittest.TestCase):
    """Tests for the BaseOAuthClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.session_storage = MagicMock(spec=SessionStorage)
        self.client = BaseOAuthClient(
            url=BASE_API_URL, session_storage=self.session_storage
        )

    @patch.object(BaseOAuthClient, "_login_using_storage", return_value=True)
    def test_login_with_storage_success(self, mock_login_using_storage):
        """Test successful login using stored session."""
        # Act
        result = self.client.login(persist_session=True)

        # Assert
        self.assertTrue(result)
        mock_login_using_storage.assert_called_once()

    @patch.object(BaseOAuthClient, "_login_using_storage", return_value=False)
    @patch.object(BaseOAuthClient, "_login_using_request")
    def test_login_with_credentials(
        self, mock_login_using_request, mock_login_using_storage
    ):
        """Test login with username and password."""

        # Arrange
        def mock_login_side_effect(*args, **kwargs):
            # Simulate the real behavior of setting _is_authenticated = True
            self.client._is_authenticated = True
            return {
                "token_type": "Bearer",
                "access_token": "access123",
                "refresh_token": "refresh456",
            }

        mock_login_using_request.side_effect = mock_login_side_effect

        # Act
        result = self.client.login(
            username="test_user", password="test_pass", persist_session=True
        )

        # Assert
        self.assertTrue(result)
        mock_login_using_storage.assert_called_once()
        mock_login_using_request.assert_called_once()
        self.session_storage.store.assert_called_once()

    def test_login_using_storage_with_valid_session(self):
        """Test _login_using_storage with valid stored session."""
        # Arrange
        mock_session = MagicMock()
        self.session_storage.load.return_value = mock_session
        self.client._test_auth_connection = MagicMock(return_value=True)

        # Act
        result = self.client._login_using_storage()

        # Assert
        self.assertTrue(result)
        self.assertTrue(self.client._is_authenticated)
        self.session_storage.load.assert_called_once()

    def test_login_using_storage_with_invalid_session(self):
        """Test _login_using_storage with invalid stored session."""
        # Arrange
        mock_session = MagicMock()
        self.session_storage.load.return_value = mock_session
        self.client._test_auth_connection = MagicMock(return_value=False)

        # Act
        with self.assertLogs(level="ERROR") as log:
            result = self.client._login_using_storage()

        # Assert
        self.assertFalse(result)
        self.assertFalse(self.client._is_authenticated)
        self.assertIn(
            "ERROR:robinhood_client.common.clients:Stored session is invalid",
            log.output[0],
        )

    def test_login_using_storage_with_no_session(self):
        """Test _login_using_storage with no stored session."""
        # Arrange
        self.session_storage.load.return_value = None

        # Act
        result = self.client._login_using_storage()

        # Assert
        self.assertFalse(result)
        self.assertFalse(self.client._is_authenticated)

    @patch.object(BaseOAuthClient, "request_post")
    def test_login_using_request_success(self, mock_request_post):
        """Test successful login using request."""
        # Arrange
        mock_request_post.return_value = {
            "token_type": "Bearer",
            "access_token": "access123",
            "refresh_token": "refresh456",
        }

        # Act
        result = self.client._login_using_request(
            username="test_user",
            password="test_pass",
            expiresIn=86400,
            scope="internal",
            device_token="device123",
            mfa_code=None,
        )

        # Assert
        self.assertEqual(result["access_token"], "access123")
        self.assertTrue(self.client._is_authenticated)
        expected_payload = {
            "client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
            "expires_in": 86400,
            "grant_type": "password",
            "password": "test_pass",
            "scope": "internal",
            "username": "test_user",
            "device_token": "device123",
            "try_passkeys": False,
            "token_request_path": "/login",
            "create_read_only_secondary_token": True,
        }
        mock_request_post.assert_called_with(
            API_LOGIN_URL, expected_payload, json_request=True
        )

    @patch.object(BaseOAuthClient, "request_post")
    def test_login_using_request_with_mfa(self, mock_request_post):
        """Test login with MFA code."""
        # Arrange
        mock_request_post.return_value = {
            "token_type": "Bearer",
            "access_token": "access123",
            "refresh_token": "refresh456",
        }

        # Act
        result = self.client._login_using_request(
            username="test_user",
            password="test_pass",
            expiresIn=86400,
            scope="internal",
            device_token="device123",
            mfa_code="123456",
        )

        # Assert
        self.assertEqual(result["access_token"], "access123")
        expected_payload = {
            "client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
            "expires_in": 86400,
            "grant_type": "password",
            "password": "test_pass",
            "scope": "internal",
            "username": "test_user",
            "device_token": "device123",
            "mfa_code": "123456",
            "try_passkeys": False,
            "token_request_path": "/login",
            "create_read_only_secondary_token": True,
        }
        mock_request_post.assert_called_with(
            API_LOGIN_URL, expected_payload, json_request=True
        )

    # TODO: Causes tests to freeze / timeout
    # @patch.object(BaseOAuthClient, "request_post")
    # def test_login_using_request_verification_workflow(self, mock_request_post):
    #     """Test login with verification workflow."""
    #     # Arrange
    #     mock_request_post.side_effect = [
    #         {"verification_workflow": {"id": "workflow123"}},
    #         {
    #             "token_type": "Bearer",
    #             "access_token": "access123",
    #             "refresh_token": "refresh456",
    #         },
    #     ]
    #     self.client._validate_sherrif_id = MagicMock()

    #     # Act
    #     result = self.client._login_using_request(
    #         username="test_user",
    #         password="test_pass",
    #         expiresIn=86400,
    #         scope="internal",
    #         device_token="device123",
    #         mfa_code=None,
    #     )

    #     # Assert
    #     self.assertEqual(result["access_token"], "access123")
    #     self.client._validate_sherrif_id.assert_called_once_with(
    #         device_token="device123", workflow_id="workflow123"
    #     )

    @patch.object(BaseOAuthClient, "request_post")
    def test_login_using_request_error_response(self, mock_request_post):
        """Test login with error response."""
        # Arrange
        mock_request_post.return_value = {"detail": "Authentication failed"}

        # Act & Assert
        with self.assertRaises(AuthenticationError) as context:
            self.client._login_using_request(
                username="test_user",
                password="test_pass",
                expiresIn=86400,
                scope="internal",
                device_token="device123",
                mfa_code=None,
            )

        self.assertEqual(str(context.exception), "Authentication failed")

    @patch.object(BaseOAuthClient, "request_post")
    def test_login_using_request_no_response(self, mock_request_post):
        """Test login with no response."""
        # Arrange
        mock_request_post.return_value = None

        # Act
        with self.assertLogs(level="ERROR") as log:
            result = self.client._login_using_request(
                username="test_user",
                password="test_pass",
                expiresIn=86400,
                scope="internal",
                device_token="device123",
                mfa_code=None,
            )

        # Assert
        self.assertFalse(result)
        self.assertIn(
            "ERROR:robinhood_client.common.clients:Login failed: No response",
            log.output[0],
        )

    @patch.object(BaseOAuthClient, "request_get")
    def test_test_auth_connection(self, mock_request_get):
        """Test _test_auth_connection method."""
        # Arrange
        mock_response = MagicMock(spec=requests.Response)
        mock_request_get.return_value = mock_response

        # Act
        with self.assertLogs(level="DEBUG") as log:
            result = self.client._test_auth_connection()

        # Assert
        self.assertTrue(result)
        mock_request_get.assert_called_once_with(
            f"{BASE_API_URL}/accounts/", {"nonzero": "true"}, json_response=False
        )
        mock_response.raise_for_status.assert_called_once()
        self.assertIn(
            "DEBUG:robinhood_client.common.clients:Testing authentication connection...",
            log.output[0],
        )

    @patch.object(BaseOAuthClient, "request_get")
    def test_test_auth_connection_non_response_object(self, mock_request_get):
        """Test _test_auth_connection method with non-Response object."""
        # Arrange
        mock_dict_response = {"status": "ok"}
        mock_request_get.return_value = mock_dict_response

        # Act
        with self.assertLogs(level="DEBUG") as log:
            result = self.client._test_auth_connection()

        # Assert
        self.assertTrue(result)
        mock_request_get.assert_called_once_with(
            f"{BASE_API_URL}/accounts/", {"nonzero": "true"}, json_response=False
        )
        self.assertIn(
            "DEBUG:robinhood_client.common.clients:Testing authentication connection...",
            log.output[0],
        )

    def test_logout(self):
        """Test logout method."""
        # Arrange
        self.client._is_authenticated = True
        self.client._session.headers["Authorization"] = "Bearer token123"

        # Act
        self.client.logout()

        # Assert
        self.assertFalse(self.client._is_authenticated)
        self.assertNotIn("Authorization", self.client._session.headers)
        self.session_storage.clear.assert_called_once()

    def test_get_access_token(self):
        """Test get_access_token method."""
        # Arrange
        self.client._session.headers["Authorization"] = "Bearer token123"

        # Act
        result = self.client.get_access_token()

        # Assert
        self.assertEqual(result, "Bearer token123")


if __name__ == "__main__":
    unittest.main()
