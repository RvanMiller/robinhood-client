from abc import ABC
from typing import Optional, List
from pydantic import BaseModel


# Base Schemas
#
class BaseRequest(BaseModel, ABC):
    pass


class BaseResponse(BaseModel, ABC):
    pass


class BaseCursorRequest(BaseRequest, ABC):
    page_size: Optional[int] = 10


class BaseCursorResponse(BaseResponse, ABC):
    next: Optional[str] = None
    previous: Optional[str] = None


# Stocks
#
class GetStockOrderRequest(BaseRequest):
    account_number: str
    order_id: str
    start_date: Optional[str] = None


class GetStockOrderResponse(BaseResponse):
    results: dict


class GetStockOrdersRequest(BaseCursorRequest):
    account_number: str
    start_date: Optional[str] = None


class GetStockOrdersResponse(BaseCursorResponse):
    results: List[dict]


# Options
#
class GetOptionOrdersRequest(BaseCursorRequest):
    symbol: str
    expirationDate: Optional[str] = None
    strike: Optional[float] = None
    optionType: Optional[str] = None


class GetOptionOrdersResponse(BaseCursorResponse):
    results: List[dict]
