from robinhood_client.common.exceptions import (
    AuthenticationError,
)
from robinhood_client.common.session import (
    AuthSession,
    SessionStorage,
    FileSystemSessionStorage,
    AWSS3SessionStorage,
)

# Import logging configuration first to ensure it's set up before other modules
from robinhood_client.common.logging import configure_logging

# Configure the default logger for the package
configure_logging()

__all__ = [
    "configure_logging",
    "AuthenticationError",
    "AuthSession",
    "SessionStorage",
    "FileSystemSessionStorage",
    "AWSS3SessionStorage",
]
