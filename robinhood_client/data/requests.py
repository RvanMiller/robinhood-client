from datetime import date
from typing import Optional
from pydantic import BaseModel


class StockOrderRequest(BaseModel):
    account_number: Optional[str] = None
    order_id: str


class StockOrderResponse(BaseModel):
    # For single order response, it's just the StockOrder itself
    # This is a wrapper for consistency
    pass  # Will be replaced with StockOrder fields or just use StockOrder directly


class StockOrdersRequest(BaseModel):
    account_number: str
    start_date: Optional[date | str] = None
    page_size: Optional[int] = 10


class OptionsOrderRequest(BaseModel):
    account_number: Optional[str] = None
    order_id: str


class OptionsOrdersRequest(BaseModel):
    account_number: str
    start_date: Optional[date | str] = None
    page_size: Optional[int] = 10
