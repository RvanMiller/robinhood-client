from datetime import date
from typing import Optional
from robinhood_client.common.schema import RobinhoodBaseModel


class StockOrderRequest(RobinhoodBaseModel):
    account_number: Optional[str] = None
    order_id: str


class StockOrderResponse(RobinhoodBaseModel):
    # For single order response, it's just the StockOrder itself
    # This is a wrapper for consistency
    pass  # Will be replaced with StockOrder fields or just use StockOrder directly


class StockOrdersRequest(RobinhoodBaseModel):
    account_number: str
    page_size: Optional[int] = 10
    start_date: Optional[date | str] = None


class OptionOrderRequest(RobinhoodBaseModel):
    account_number: Optional[str] = None
    order_id: str


class OptionOrdersRequest(RobinhoodBaseModel):
    account_number: str
    start_date: Optional[date | str] = None
    page_size: Optional[int] = 10
