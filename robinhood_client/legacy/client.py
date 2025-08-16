"""The main client for interacting with the Robinhood API."""

# flake8: noqa
from src.robinhood_client.schemas import *
from src.robinhood_client.helper import login_required, request_get_ex
from src.robinhood_client.urls import orders_url
from src.robinhood_client.authentication import login, logout


class RobinhoodClient:
    """A facade for the Robinhood API."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def login(self):
        # Logic for logging in to Robinhood
        pass

    def logout(self):
        # Logic for logging out of Robinhood
        pass

    def get_account_info(self):
        # Logic for getting account information
        pass

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
        url = orders_url(account_number=request.account_number,
                        start_date=request.start_date)
        res = request_get_ex(url, params={
            "order_id": request.order_id,
        })
        return GetStockOrderResponse(**res)

    def get_all_stock_orders(self, request: GetStockOrdersRequest) -> GetStockOrdersResponse:
        """Gets a list of all stock orders for an account with pagination support.
        
        Args:
            request: A GetStockOrdersRequest containing:
                account_number: The Robinhood account number
                start_date: Optional date filter for orders
                page_size: Optional number of results per page (default: 10)
                
        Returns:
            GetStockOrdersResponse with paginated order results
        """
        url = orders_url(account_number=request.account_number,
                        start_date=request.start_date)
        res = request_get_ex(url, params={
            "account_number": request.account_number,
            "start_date": request.start_date,
            "page_size": request.page_size,
        })
        return GetStockOrdersResponse(**res)

    def get_all_option_orders(self):
        # Logic for getting all option orders
        pass

    def get_all_crypto_orders(self):
        # Logic for getting all crypto orders
        pass
