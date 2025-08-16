"""Client for retrieving Stock data."""

from robinhood_client.common.clients import BaseOAuthClient
from robinhood_client.common.session import SessionStorage

from .requests import GetStockOrderRequest, GetStockOrderResponse, GetStockOrdersRequest, GetStockOrdersResponse


class OrdersDataClient(BaseOAuthClient):
    """Client for retrieving Stock data."""

    def __init__(self, session_storage: SessionStorage):
        super().__init__(session_storage)

    def get_stock_order(self, request: GetStockOrderRequest) -> GetStockOrderResponse:
        """Gets information for a specific stock order.
        
        Args:
            request: A GetStockOrderRequest containing:
                account_number: The Robinhood account number
                order_id: The ID of the order to retrieve
                start_date: Optional date to filter orders
                
        Returns:
            GetStockOrderResponse with the order information
        """
        params = {}
        url = f"/orders/{request.order_id}/"
        if request.account_number is not None:
            params["account_number"] = request.account_number

        res = self.request_get(url, params=params)
        return GetStockOrderResponse(**res)

    def get_stock_orders(self, request: GetStockOrdersRequest) -> GetStockOrdersResponse:
        """Gets a list of all stock orders for an account with pagination support.
        
        Args:
            request: A GetStockOrdersRequest containing:
                account_number: The Robinhood account number
                start_date: Optional date filter for orders
                page_size: Optional number of results per page (default: 10)
                
        Returns:
            GetStockOrdersResponse with paginated order results
        """
        params = {}
        url = f"/orders/{request.order_id}/"
        if request.account_number is not None:
            params["account_number"] = request.account_number
        if request.start_date is not None:
            params["start_date"] = request.start_date
        if request.page_size is not None:
            params["page_size"] = request.page_size

        res = self.request_get(url, params=params)
        return GetStockOrdersResponse(**res)
    