from typing import Optional
from pydantic import BaseModel
from robinhood_client.common.schema import StockOrder


class StockOrderRequest(BaseModel):
    account_number: Optional[str] = None
    order_id: str


class StockOrderResponse(BaseModel):
    # For single order response, it's just the StockOrder itself
    # This is a wrapper for consistency
    pass  # Will be replaced with StockOrder fields or just use StockOrder directly


class StockOrdersRequest(BaseModel):
    account_number: str
    start_date: str | None = None
    page_size: int | None = 10


class StockOrdersResponse(BaseModel):
    results: list[StockOrder]
    next: str | None = None
    previous: str | None = None
