"""Client for retrieving Stock data."""

from robinhood_client.common.clients import BaseOAuthClient
from robinhood_client.common.session import SessionStorage
from robinhood_client.common.constants import BASE_API_URL
from robinhood_client.common.schema import StockOrder

from .requests import (
    StockOrderRequest,
    StockOrdersRequest,
    StockOrdersResponse,
)


class OrdersDataClient(BaseOAuthClient):
    """Client for retrieving Stock data."""

    def __init__(self, session_storage: SessionStorage):
        super().__init__(url=BASE_API_URL, session_storage=session_storage)

    def get_stock_order(self, request: StockOrderRequest) -> StockOrder:
        """Gets information for a specific stock order.

        Args:
            request: A StockOrderRequest containing:
                account_number: The Robinhood account number
                order_id: The ID of the order to retrieve
                start_date: Optional date to filter orders

        Returns:
            StockOrder with the order information
        """
        params = {}
        endpoint = f"/orders/{request.order_id}/"
        if request.account_number is not None:
            params["account_number"] = request.account_number

        res = self.request_get(endpoint, params=params)
        return StockOrder(**res)

    def get_stock_orders(self, request: StockOrdersRequest) -> StockOrdersResponse:
        """Gets a list of all stock orders for an account with pagination support.

        Args:
            request: A StockOrdersRequest containing:
                account_number: The Robinhood account number
                start_date: Optional date filter for orders (accepts string or date object)
                page_size: Optional pagination page size

        Returns:
            StockOrdersResponse with paginated order results
        """
        params = {"account_number": request.account_number}
        endpoint = "/orders/"

        if request.start_date is not None:
            # Convert date object to string if needed, API expects string format
            if hasattr(request.start_date, 'isoformat'):
                params["start_date"] = request.start_date.isoformat()
            else:
                params["start_date"] = request.start_date

        if request.page_size is not None:
            params["page_size"] = request.page_size
        else:
            # Add default page_size only if not provided in request
            params["page_size"] = 10

        res = self.request_get(endpoint, params=params)
        return StockOrdersResponse(**res)
