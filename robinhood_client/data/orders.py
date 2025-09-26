"""Client for retrieving Stock data."""

from robinhood_client.common.clients import BaseOAuthClient
from robinhood_client.common.session import SessionStorage
from robinhood_client.common.constants import BASE_API_URL
from robinhood_client.common.schema import StockOrder, StockOrdersPageResponse
from robinhood_client.common.cursor import ApiCursor, PaginatedResult

from .instruments import InstrumentCacheClient
from .requests import (
    StockOrderRequest,
    StockOrdersRequest,
)


class OrdersDataClient(BaseOAuthClient):
    """Client for retrieving Stock data."""

    def __init__(self, session_storage: SessionStorage):
        super().__init__(url=BASE_API_URL, session_storage=session_storage)
        self._instrument_client = InstrumentCacheClient(session_storage)

    def get_stock_order(self, request: StockOrderRequest) -> StockOrder:
        """Gets information for a specific stock order.

        Args:
            request: A StockOrderRequest containing:
                account_number: The Robinhood account number
                order_id: The ID of the order to retrieve
                start_date: Optional date to filter orders
                resolve_symbols: Whether to resolve instrument symbols (default: True)

        Returns:
            StockOrder with the order information (symbol populated if resolve_symbols=True)
        """
        params = {}
        endpoint = f"/orders/{request.order_id}/"
        if request.account_number is not None:
            params["account_number"] = request.account_number

        res = self.request_get(endpoint, params=params)
        order = StockOrder(**res)

        # Resolve symbol if requested
        if request.resolve_symbols:
            symbol = self._instrument_client.get_symbol_by_instrument_url(
                order.instrument
            )
            if symbol:
                order.symbol = symbol

        return order

    def get_stock_orders(
        self, request: StockOrdersRequest
    ) -> PaginatedResult[StockOrder]:
        """Gets a cursor-based paginated result for stock orders.

        This method returns a PaginatedResult object that supports both direct access
        to the current page and cursor-based iteration through all pages.

        Args:
            request: A StockOrdersRequest containing:
                account_number: The Robinhood account number
                start_date: Optional date filter for orders (accepts string or date object)
                page_size: Optional pagination page size
                resolve_symbols: Whether to resolve instrument symbols (default: True)

        Returns:
            PaginatedResult[StockOrder] that can be used for:
            - Direct access: result.results, result.next, result.previous
            - Iteration: for order in result: ...
            - Advanced pagination: result.cursor().next(), result.cursor().all()

        Example:
            >>> request = StockOrdersRequest(account_number="123")
            >>> result = client.get_stock_orders(request)
            >>>
            >>> # Access current page
            >>> current_orders = result.results
            >>>
            >>> # Iterate through all pages
            >>> for order in result:
            >>>     print(f"Order {order.id}: {order.state} - {order.symbol}")
            >>>
            >>> # Manual pagination
            >>> cursor = result.cursor()
            >>> if cursor.has_next():
            >>>     next_page = cursor.next()
            >>>
            >>> # Get all orders from all pages
            >>> all_orders = result.cursor().all()
        """
        params = {"account_number": request.account_number}
        endpoint = "/orders/"

        if request.start_date is not None:
            # Convert date object to string if needed, API expects string format
            if hasattr(request.start_date, "isoformat"):
                params["start_date"] = request.start_date.isoformat()
            else:
                params["start_date"] = request.start_date

        if request.page_size is not None:
            params["page_size"] = request.page_size
        else:
            # Add default page_size only if not provided in request
            params["page_size"] = 10

        # Create a cursor for this request with symbol resolution
        if request.resolve_symbols:
            cursor = self._create_symbol_resolving_cursor(endpoint, params)
        else:
            cursor = ApiCursor(
                client=self,
                endpoint=endpoint,
                response_model=StockOrdersPageResponse,
                base_params=params,
            )

        return PaginatedResult(cursor)

    def _create_symbol_resolving_cursor(
        self, endpoint: str, base_params: dict
    ) -> ApiCursor[StockOrder]:
        """Create a cursor that automatically resolves symbols for orders.

        Args:
            endpoint: The API endpoint
            base_params: Base parameters for the request

        Returns:
            ApiCursor with symbol resolution
        """

        class SymbolResolvingApiCursor(ApiCursor[StockOrder]):
            def __init__(self, orders_client, *args, **kwargs):
                self._orders_client = orders_client
                super().__init__(*args, **kwargs)

            def _fetch_current_page(self):
                """Override to resolve symbols after fetching."""
                super()._fetch_current_page()
                if (
                    self._current_page
                    and self._current_page.results
                    and hasattr(self._orders_client, "_instrument_client")
                ):
                    # Resolve symbols for all orders in this page
                    for order in self._current_page.results:
                        if not order.symbol:  # Only resolve if not already set
                            try:
                                symbol = self._orders_client._instrument_client.get_symbol_by_instrument_url(
                                    order.instrument
                                )
                                if symbol:
                                    order.symbol = symbol
                            except Exception:
                                # Silently handle any errors in symbol resolution
                                # The order data is still valid without the symbol
                                pass

        return SymbolResolvingApiCursor(
            self,
            client=self,
            endpoint=endpoint,
            response_model=StockOrdersPageResponse,
            base_params=base_params,
        )
