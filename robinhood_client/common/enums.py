"""Contains all common constants used in Robinhood Client."""

from enum import Enum


class CurrencyCode(Enum):
    """Enumeration for notional currencies."""

    USD = "USD"
    # TODO: Add other currencies that Robinhood supports


class OrderType(Enum):
    """Enumeration for order types."""

    MARKET = "market"
    LIMIT = "limit"
    # TODO: Add others
    # STOP = "stop"
    # STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Enumeration for order sides."""

    BUY = "buy"
    SELL = "sell"


class OrderState(Enum):
    """Enumeration for order states."""

    CLOSED = "closed"
    CANCELLED = "cancelled"
    FILLED = "filled"
    # TODO: Add others


class TimeInForce(Enum):
    """Enumeration for time in force options."""

    GFD = "gfd"  # Good for day
    GTC = "gtc"  # Good till cancelled
    # TODO: Add others


class TriggerType(Enum):
    """Enumeration for trigger types."""

    IMMEDIATE = "immediate"
    STOP = "stop"
    # TODO: Add others


class PositionEffect(Enum):
    """Enumeration for position effect options."""

    OPEN = "open"
    CLOSE = "close"
