"""Contains all common constants used in Robinhood Client."""

from enum import Enum


class OrderType(Enum):
    """Enumeration for order types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
