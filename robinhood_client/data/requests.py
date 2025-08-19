from typing import Optional
from pydantic import BaseModel


class StockOrderRequest(BaseModel):
    account_number: Optional[str] = None
    order_id: str


class StockOrderResponse(BaseModel):
    id: str
    instrument: dict
    quantity: int
    price: float
    side: str
    status: str
    created_at: str
    updated_at: str


class StockOrdersRequest(BaseModel):
    account_number: str
    start_date: str | None = None
    page_size: int | None = 10


class StockOrdersResponse(BaseModel):
    results: list[StockOrderResponse]
    next: str | None
    previous: str | None
