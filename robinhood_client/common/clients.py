"""Base clients used in the Robinhood Client library."""

from getpass import getpass
import logging
import time
import requests

from abc import ABC
from requests import Response, Session
from urllib.parse import urljoin

from .auth import generate_device_token
from .exceptions import AuthenticationError
from .constants import BASE_API_URL, API_LOGIN_URL
from .session import AuthSession, SessionStorage

# Get logger for this module
logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Base class for all Robinhood clients without authentication."""

    def __init__(self):
        """Initialize the base client."""
        self._session = Session()
        self._session.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate,br",
            "Accept-Language": "en-US,en;q=1",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.431.4",
            "Connection": "keep-alive",
            "User-Agent": "*",
        }

    def _join_url(self, url: str) -> str:
        """Join a URL with the base URL if applicable.

        This method is meant to be overridden by subclasses that have a base URL.
        Base implementation returns the URL unchanged.

        Args:
            url: The URL or endpoint path

        Returns:
            The full URL
        """
        return url

    def request_get(
        self,
        url: str,
        params: dict = None,
        json_response: bool = True,
    ) -> list[dict] | Response:
        logger.debug("Making GET request to %s", url)
        res = None
        try:
            full_url = self._join_url(url)
            res = self._session.get(full_url, params=params)
            res.raise_for_status()
            if json_response:
                return res.json()
            else:
                return res
        except Exception as message:
            logger.error("Error in BaseClient request_get: %s", message)
            return res

    def request_post(
        self,
        url: str,
        payload: dict = None,
        json_request: bool = False,
        json_response: bool = True,
        timeout: int = 16,
    ):
        logger.debug("Making POST request to %s", url)
        res = None
        try:
            full_url = self._join_url(url)
            if json_request:
                self._session.headers.update({"Content-Type": "application/json"})
                res = self._session.post(full_url, json=payload, timeout=timeout)
                self._session.headers.update(
                    {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
                )
            else:
                res = self._session.post(full_url, data=payload, timeout=timeout)
            if res.status_code not in [
                200,
                201,
                202,
                204,
                301,
                302,
                303,
                304,
                307,
                400,
                401,
                402,
                403,
            ]:
                raise Exception(
                    "Error code from Robinhood API: " + str(res.status_code)
                )
        except Exception as message:
            logger.error("Error in BaseClient request_post: %s", message)
        if json_response:
            return res.json()
        else:
            return res


class BaseOAuthClient(BaseClient):
    """Base class for all Robinhood clients with OAuth authentication."""

    def __init__(self, url: str, session_storage: SessionStorage):
        super().__init__()
        self._url = url
        self._is_authenticated = False
        self._session_storage = session_storage

    def request_get(
        self,
        url: str,
        params: dict = None,
        json_response: bool = True,
    ):
        # Ensure Authorization header is set for authenticated requests
        if self._is_authenticated and self._session.headers.get("Authorization"):
            self._session.headers["Authorization"] = self._session.headers.get(
                "Authorization"
            )
        return super().request_get(url, params, json_response=json_response)

    def request_post(
        self,
        url: str,
        payload: dict = None,
        json_request: bool = False,
        json_response: bool = True,
        timeout: int = 16,
    ):
        # Ensure Authorization header is set for authenticated requests
        if self._is_authenticated and self._session.headers.get("Authorization"):
            self._session.headers["Authorization"] = self._session.headers.get(
                "Authorization"
            )
        return super().request_post(
            url,
            payload,
            json_request=json_request,
            json_response=json_response,
            timeout=timeout,
        )

    def _join_url(self, endpoint: str) -> str:
        """Join the base URL with an endpoint using urllib.parse.urljoin.

        Args:
            endpoint: The API endpoint path (with or without leading slash)

        Returns:
            The full URL
        """
        # If the URL is already absolute, return it as is
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint

        # Ensure endpoint starts with a slash
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        # urljoin needs the base URL to end with a slash to preserve the path
        base = self._url
        if not base.endswith("/"):
            base = base + "/"

        return urljoin(base, endpoint.lstrip("/"))

    def login(
        self,
        username=None,
        password=None,
        expiresIn=86400,
        scope="internal",
        persist_session=True,
        mfa_code=None,
    ) -> bool:
        """This function will effectively log the user into robinhood by getting
        an authentication token and saving it to the session header.

        """
        logger.debug("Logging in to Robinhood...")

        if persist_session:
            logger.debug("Session persistence is enabled.")
            if self._login_using_storage():
                logger.info("Using existing Robinhood session.")
                return True

        logger.debug("No stored session found. Proceeding with login.")
        device_token = generate_device_token()
        logger.debug("Generated device token: %s", device_token)

        response = self._login_using_request(
            username=username,
            password=password,
            expiresIn=expiresIn,
            scope=scope,
            mfa_code=mfa_code,
            device_token=device_token,
        )

        if self._is_authenticated and persist_session:
            logger.debug("Saving authentication session.")
            self._session_storage.store(
                AuthSession(
                    token_type=response["token_type"],
                    access_token=response["access_token"],
                    refresh_token=response["refresh_token"],
                    device_token=device_token,
                )
            )

        return True

    def _login_using_storage(self) -> bool:
        loaded_session = self._session_storage.load()
        if loaded_session is None:
            return False

        logger.debug("Attempting to log in using stored session...")
        self._session.headers.update(
            {
                "Authorization": f"{loaded_session.token_type} {loaded_session.access_token}"
            }
        )
        if self._test_auth_connection():
            self._is_authenticated = True
            logger.debug("Loaded session from storage.")
            return True
        else:
            logger.error("Stored session is invalid. Failed to authenticate.")
            return False

    def _login_using_request(
        self,
        username=None,
        password=None,
        *,
        expiresIn,
        scope,
        device_token,
        mfa_code,
    ) -> dict | AuthenticationError:
        logger.debug("Attempting to log in normally...")

        payload = {}
        if not username:
            username = input("Robinhood username: ")
            payload["username"] = username

        if not password:
            password = getpass("Robinhood password: ")
            payload["password"] = password

        payload = {
            "client_id": "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
            "expires_in": expiresIn,
            "grant_type": "password",
            "password": password,
            "scope": scope,
            "username": username,
            "device_token": device_token,
            "try_passkeys": False,
            "token_request_path": "/login",
            "create_read_only_secondary_token": True,
        }

        if mfa_code:
            payload["mfa_code"] = mfa_code

        response = self.request_post(API_LOGIN_URL, payload, json_request=True)

        if response is None:
            logger.error("Login failed: No response from Robinhood API.")
            return False

        if "verification_workflow" in response:
            logger.info(
                "Verification workflow required. Please check your Robinhood Mobile app."
            )
            workflow_id = response["verification_workflow"]["id"]
            self._validate_sheriff_id(
                device_token=device_token, workflow_id=workflow_id
            )
            response = self.request_post(API_LOGIN_URL, payload)

        if "access_token" in response:
            token = "{0} {1}".format(response["token_type"], response["access_token"])
            self._session.headers.update({"Authorization": token})
            self._is_authenticated = True
            logger.info("Logged in to Robinhood successfully.")
        else:
            if "detail" in response:
                logger.error("Login failed: %s", response["detail"])
                raise AuthenticationError(response["detail"])
            logger.error("Login failed: %s", response)
            raise AuthenticationError(f"Received an error response {response}")

        return response

    def _test_auth_connection(self) -> bool:
        logger.debug("Testing authentication connection...")
        res = self.request_get(
            f"{BASE_API_URL}/accounts/",
            {"nonzero": "true"},
            json_response=False,
        )
        if isinstance(res, Response):
            res.raise_for_status()
        return True

    def logout(self):
        """Logs out of Robinhood by clearing session data.

        :returns: None

        """
        self._is_authenticated = False
        self._session.headers.pop("Authorization", None)
        self._session_storage.clear()
        logger.info("Logged out of Robinhood successfully.")

    def get_access_token(self):
        """Retrieve the access token from the session."""
        return self._session.headers.get("Authorization")

    def _get_sheriff_id(self, data):
        """Extracts the sheriff verification ID from the response."""
        if "id" in data:
            return data["id"]
        raise Exception("Error: No verification ID returned in user-machine response")

    def _validate_sheriff_id(self, device_token: str, workflow_id: str):
        """Handles Robinhood's verification workflow."""
        logger.debug("Validating sheriff challenge...")
        pathfinder_url = f"{BASE_API_URL}/pathfinder/user_machine/"
        machine_payload = {
            "device_id": device_token,
            "flow": "suv",
            "input": {"workflow_id": workflow_id},
        }
        machine_data = self.request_post(
            url=pathfinder_url, payload=machine_payload, json_request=True
        )

        machine_id = machine_data.get("id", None)
        inquiries_url = f"{BASE_API_URL}/pathfinder/inquiries/{machine_id}/user_view/"

        start_time = time.time()

        while time.time() - start_time < 120:  # 2-minute timeout
            time.sleep(5)
            inquiries_response = self.request_get(inquiries_url)

            if not inquiries_response:  # Handle case where response is None
                logger.warning("Error: No response from Robinhood API. Retrying...")
                continue

            if (
                "context" in inquiries_response
                and "sheriff_challenge" in inquiries_response["context"]
            ):
                challenge = inquiries_response["context"]["sheriff_challenge"]
                challenge_type = challenge["type"]
                challenge_status = challenge["status"]
                challenge_id = challenge["id"]
                if challenge_type == "prompt":
                    logger.info("Waiting for approval from Robinhood Mobile app...")
                    prompt_url = (
                        f"{BASE_API_URL}/push/{challenge_id}/get_prompts_status/"
                    )
                    while True:
                        time.sleep(5)
                        prompt_challenge_status = self.request_get(url=prompt_url)
                        if prompt_challenge_status["challenge_status"] == "validated":
                            break
                    break

                if challenge_status == "validated":
                    logger.info("Verification successful!")
                    break  # Stop polling once verification is complete

                if challenge_type in ["sms", "email"] and challenge_status == "issued":
                    user_code = input(
                        f"Enter the {challenge_type} verification code sent to your device: "
                    )
                    challenge_url = f"{BASE_API_URL}/challenge/{challenge_id}/respond/"
                    challenge_payload = {"response": user_code}
                    challenge_response = self.request_post(
                        url=challenge_url, payload=challenge_payload, json_request=True
                    )

                    if challenge_response.get("status") == "validated":
                        break

        # **Now poll the workflow status to confirm final approval**
        inquiries_url = f"{BASE_API_URL}/pathfinder/inquiries/{machine_id}/user_view/"

        retry_attempts = 5  # Allow up to 5 retries in case of 500 errors
        while time.time() - start_time < 120:  # 2-minute timeout
            try:
                inquiries_payload = {
                    "sequence": 0,
                    "user_input": {"status": "continue"},
                }
                inquiries_response = self.request_post(
                    url=inquiries_url, payload=inquiries_payload, json_request=True
                )
                if (
                    "type_context" in inquiries_response
                    and inquiries_response["type_context"]["result"]
                    == "workflow_status_approved"
                ):
                    logger.info("Verification successful!")
                    return
                else:
                    # Increase delay between requests to prevent rate limits
                    time.sleep(5)
            except requests.exceptions.RequestException as e:
                time.sleep(5)
                logger.error("API request failed: %s", e)
                retry_attempts -= 1
                if retry_attempts == 0:
                    logger.error("Max retries reached. Login failed: %s", str(e))
                    raise AuthenticationError(
                        f"Max retries reached. Login failed: {str(e)}"
                    )
                logger.debug("Retrying workflow status check...")
                continue

            # Handle None response
            if not inquiries_response:
                time.sleep(5)
                logger.warning("Error: No response from Robinhood API. Retrying...")
                retry_attempts -= 1
                if retry_attempts == 0:
                    logger.error("Max retries reached. Login verification failed.")
                    raise AuthenticationError(
                        "Max retries reached. Login verification failed."
                    )
                continue

            workflow_status = inquiries_response.get("verification_workflow", {}).get(
                "workflow_status"
            )

            if workflow_status == "workflow_status_approved":
                logger.info("Workflow status approved! Proceeding with login...")
                return
            elif workflow_status == "workflow_status_internal_pending":
                logger.info("Still waiting for Robinhood to finalize login approval...")
            else:
                retry_attempts -= 1
                if retry_attempts == 0:
                    logger.error("Max retries reached. Unable to confirm verification.")
                    raise AuthenticationError(
                        "Max retries reached. Unable to confirm verification."
                    )

        logger.error("Timeout reached. Unable to confirm verification.")
        raise AuthenticationError("Timeout reached. Unable to confirm verification.")
