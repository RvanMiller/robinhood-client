from robinhood_client.common.exceptions import (
    AuthenticationError,
)
from robinhood_client.common.session import (
    AuthSession,
    SessionStorage,
    FileSystemSessionStorage,
    AWSS3SessionStorage,
)
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import (
    StockOrderRequest,
    StockOrdersRequest,
    OptionOrderRequest,
    OptionOrdersRequest,
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
    "OrdersDataClient",
    "StockOrderRequest",
    "StockOrdersRequest",
    "OptionOrderRequest",
    "OptionOrdersRequest",
]
