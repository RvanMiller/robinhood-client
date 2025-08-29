from typing import List, Optional

from robinhood_client.common.schema import StockOrder
from robinhood_client.data.models.base import (
    BaseCursorRequest,
    BaseCursorResponse,
    BaseRequest,
    BaseResponse,
)


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
    results: list[StockOrder]


# Options
#
class GetOptionOrdersRequest(BaseCursorRequest):
    symbol: str
    expirationDate: Optional[str] = None
    strike: Optional[float] = None
    optionType: Optional[str] = None


class GetOptionOrdersResponse(BaseCursorResponse):
    results: List[dict]
