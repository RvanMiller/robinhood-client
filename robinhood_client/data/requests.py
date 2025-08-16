from typing import Optional
from pydantic import BaseModel


class GetStockOrderRequest(BaseModel):
    account_number: Optional[str] = None
    order_id: str


class GetStockOrderResponse(BaseModel):
    id: str
    instrument: dict
    quantity: int
    price: float
    side: str
    status: str
    created_at: str
    updated_at: str


class GetStockOrdersRequest(BaseModel):
    account_number: str
    start_date: str | None = None
    page_size: int | None = 10


class GetStockOrdersResponse(BaseModel):
    results: list[GetStockOrderResponse]
    next: str | None
    previous: str | None