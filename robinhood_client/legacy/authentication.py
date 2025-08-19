"""Contains all functions for the purpose of logging in and out to Robinhood."""

import getpass
import os
import pickle
import time
import secrets
import logging
import requests

from .constants import BASE_API_URL
from .exceptions import AuthenticationError
from .helper import (
    get_session,
    set_login_state,
    update_session,
    request_get,
    request_post,
    login_required,
)
from .urls import challenge_url, login_url, positions_url

# Get logger for this module
logger = logging.getLogger(__name__)


def login(
    username=None,
    password=None,
    expiresIn=86400,
    scope="internal",
    store_session=True,
    mfa_code=None,
    pickle_path="",
    pickle_name="",
):
    """This function will effectively log the user into robinhood by getting an
    authentication token and saving it to the session header. By default, it
    will store the authentication token in a pickle file and load that value
    on subsequent logins.

    :param username: The username for your robinhood account, usually your email.
        Not required if credentials are already cached and valid.
    :type username: Optional[str]
    :param password: The password for your robinhood account. Not required if
        credentials are already cached and valid.
    :type password: Optional[str]
    :param expiresIn: The time until your login session expires. This is in seconds.
    :type expiresIn: Optional[int]
    :param scope: Specifies the scope of the authentication.
    :type scope: Optional[str]
    :param store_session: Specifies whether to save the log in authorization
        for future log ins.
    :type store_session: Optional[boolean]
    :param mfa_code: MFA token if enabled.
    :type mfa_code: Optional[str]
    :param pickle_path: Allows users to specify the path of the pickle file.
        Accepts both relative and absolute paths.
    :param pickle_name: Allows users to name Pickle token file in order to switch
        between different accounts without having to re-login every time.
    :returns:  None

    """
    logger.info("Logging in to Robinhood...")
    device_token = _generate_device_token()
    home_dir = os.path.expanduser("~")
    data_dir = os.path.join(home_dir, ".tokens")
    logger.debug("Using data directory: %s", data_dir)

    if pickle_path:
        if not os.path.isabs(pickle_path):
            # normalize relative paths
            pickle_path = os.path.normpath(os.path.join(os.getcwd(), pickle_path))
        data_dir = pickle_path

    if not os.path.exists(data_dir):
        logger.debug("Creating data directory: %s", data_dir)
        os.makedirs(data_dir)

    creds_file = "robinhood" + pickle_name + ".pickle"
    pickle_path = os.path.join(data_dir, creds_file)

    url = login_url()
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

    # If authentication has been stored in pickle file then load it. Stops login server from being pinged so much.
    if os.path.isfile(pickle_path):
        # If store_session has been set to false then delete the pickle file, otherwise try to load it.
        # Loading pickle file will fail if the acess_token has expired.
        if store_session:
            try:
                with open(pickle_path, "rb") as f:
                    logger.debug("Loading existing authentication session.")
                    pickle_data = pickle.load(f)
                    access_token = pickle_data["access_token"]
                    token_type = pickle_data["token_type"]

                    # Set device_token to be the original device token when first logged in.
                    pickle_device_token = pickle_data["device_token"]
                    payload["device_token"] = pickle_device_token

                    # Set login status to True in order to try and get account info.
                    set_login_state(True)
                    update_session(
                        "Authorization", "{0} {1}".format(token_type, access_token)
                    )

                    # Try to load account profile to check that authorization token is still valid.
                    res = request_get(
                        positions_url(),
                        "pagination",
                        {"nonzero": "true"},
                        jsonify_data=False,
                    )
                    res.raise_for_status()
                    logger.info("Successfully logged in to Robinhood.")
                    return True
            except Exception:
                logger.warning(
                    "Authentication token may be expired - logging in normally."
                )
                set_login_state(False)
                update_session("Authorization", None)
        else:
            os.remove(pickle_path)

    # Try to log in normally.
    if not username:
        username = input("Robinhood username: ")
        payload["username"] = username

    if not password:
        password = getpass.getpass("Robinhood password: ")
        payload["password"] = password

    data = request_post(url, payload)
    # Handle case where mfa or challenge is required.
    if data:
        if "verification_workflow" in data:
            logger.info(
                "Verification workflow required. Please check your Robinhood Mobile app."
            )
            workflow_id = data["verification_workflow"]["id"]
            _validate_sherrif_id(device_token=device_token, workflow_id=workflow_id)
            data = request_post(url, payload)
        # Update Session data with authorization or raise exception with the information present in data.
        if "access_token" in data:
            token = "{0} {1}".format(data["token_type"], data["access_token"])
            update_session("Authorization", token)
            set_login_state(True)
            logger.debug("Logged in with existing session.")
            if store_session:
                logger.debug("Saving authentication session.")
                with open(pickle_path, "wb") as f:
                    pickle.dump(
                        {
                            "token_type": data["token_type"],
                            "access_token": data["access_token"],
                            "refresh_token": data["refresh_token"],
                            "device_token": payload["device_token"],
                        },
                        f,
                    )
        else:
            if "detail" in data:
                raise AuthenticationError(data["detail"])
            raise AuthenticationError(f"Received an error response {data}")
    else:
        raise AuthenticationError(
            "Trouble connecting to Robinhood API. Please check your Internet connection."
        )
    logger.info("Successfully logged in to Robinhood.")
    return True


@login_required
def logout():
    """Logs out of Robinhood by clearing session data.

    :returns: None

    """
    set_login_state(False)
    update_session("Authorization", None)
    logger.info("Logged out of Robinhood successfully.")


@login_required
def get_token():
    """Retrieves the current authentication token.

    :returns: The current authentication token or None if not logged in.

    """
    return get_session("Authorization")


def _respond_to_challenge(challenge_id, sms_code):
    """This function will post to the challenge url.

    :param challenge_id: The challenge id.
    :type challenge_id: str
    :param sms_code: The sms code.
    :type sms_code: str
    :returns:  The response from requests.

    """
    url = challenge_url(challenge_id)
    payload = {"response": sms_code}
    return request_post(url, payload)


def _generate_device_token():
    """Generates a cryptographically secure device token."""
    rands = [secrets.randbelow(256) for _ in range(16)]
    token = ""
    for i, r in enumerate(rands):
        token += f"{r:02x}"
        if i in [3, 5, 7, 9]:
            token += "-"
    return token


def _get_sherrif_id(data):
    """Extracts the sheriff verification ID from the response."""
    if "id" in data:
        return data["id"]
    raise AuthenticationError("No verification ID returned in user-machine response")


def _validate_sherrif_id(device_token: str, workflow_id: str):
    """Handles Robinhood's verification workflow, including email, SMS, and app-based approvals."""
    logger.debug("Validating sheriff challenge...")
    pathfinder_url = f"{BASE_API_URL}/pathfinder/user_machine/"
    machine_payload = {
        "device_id": device_token,
        "flow": "suv",
        "input": {"workflow_id": workflow_id},
    }
    machine_data = request_post(url=pathfinder_url, payload=machine_payload, json=True)

    machine_id = _get_sherrif_id(machine_data)
    inquiries_url = f"{BASE_API_URL}/pathfinder/inquiries/{machine_id}/user_view/"

    start_time = time.time()

    while time.time() - start_time < 120:  # 2-minute timeout
        time.sleep(5)
        inquiries_response = request_get(inquiries_url)

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
                prompt_url = f"{BASE_API_URL}/push/{challenge_id}/get_prompts_status/"
                while True:
                    time.sleep(5)
                    prompt_challenge_status = request_get(url=prompt_url)
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
                challenge_response = request_post(
                    url=challenge_url, payload=challenge_payload
                )

                if challenge_response.get("status") == "validated":
                    break

    # **Now poll the workflow status to confirm final approval**
    inquiries_url = f"{BASE_API_URL}/pathfinder/inquiries/{machine_id}/user_view/"

    retry_attempts = 5  # Allow up to 5 retries in case of 500 errors
    while time.time() - start_time < 120:  # 2-minute timeout
        try:
            inquiries_payload = {"sequence": 0, "user_input": {"status": "continue"}}
            inquiries_response = request_post(
                url=inquiries_url, payload=inquiries_payload, json=True
            )
            if (
                "type_context" in inquiries_response
                and inquiries_response["type_context"]["result"]
                == "workflow_status_approved"
            ):
                logger.info("Verification successful!")
                return
            else:
                time.sleep(
                    5
                )  # **Increase delay between requests to prevent rate limits**
        except requests.exceptions.RequestException as e:
            time.sleep(5)
            logger.error("API request failed: %s", e)
            retry_attempts -= 1
            if retry_attempts == 0:
                raise AuthenticationError(
                    f"Max retries reached. Login failed: {str(e)}"
                )
            logger.info("Retrying workflow status check...")
            continue

        if not inquiries_response:  # Handle None response
            time.sleep(5)
            logger.warning("Error: No response from Robinhood API. Retrying...")
            retry_attempts -= 1
            if retry_attempts == 0:
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
                raise AuthenticationError(
                    "Max retries reached. Unable to confirm verification."
                )

    raise AuthenticationError("Timeout reached. Unable to confirm verification.")
