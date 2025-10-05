"""Client for retrieving Stock data."""

from robinhood_client.common.clients import BaseOAuthClient
from robinhood_client.common.session import SessionStorage
from robinhood_client.common.constants import BASE_API_URL
from robinhood_client.common.schema import (
    StockOrder,
    StockOrdersPageResponse,
    OptionsOrder,
    OptionsOrdersPageResponse,
)
from robinhood_client.common.cursor import ApiCursor, PaginatedResult

from .instruments import InstrumentCacheClient
from .requests import (
    StockOrderRequest,
    StockOrdersRequest,
    OptionOrderRequest,
    OptionOrdersRequest,
)


class OrdersDataClient(BaseOAuthClient):
    """Client for retrieving Stock and Options data."""

    _resolve_symbols: bool = True

    def __init__(
        self, session_storage: SessionStorage = None, resolve_symbols: bool = True
    ):
        if session_storage is None:
            from robinhood_client.common.session import FileSystemSessionStorage

            session_storage = FileSystemSessionStorage()
        super().__init__(url=BASE_API_URL, session_storage=session_storage)
        self._resolve_symbols = resolve_symbols
        self._instrument_client = InstrumentCacheClient(session_storage)

    # --- Stock Orders ---

    def get_stock_order(self, request: StockOrderRequest) -> StockOrder:
        """Gets information for a specific stock order."""
        params = {}
        endpoint = f"/orders/{request.order_id}/"
        if request.account_number is not None:
            params["account_number"] = request.account_number

        res = self.request_get(endpoint, params=params)
        order = StockOrder(**res)

        # Resolve symbol if requested
        if self._resolve_symbols:
            symbol = self._instrument_client.get_symbol_by_instrument_url(
                order.instrument
            )
            if symbol:
                order.symbol = symbol

        return order

    def get_stock_orders(
        self, request: StockOrdersRequest
    ) -> PaginatedResult[StockOrder]:
        """Gets a cursor-based paginated result for stock orders."""
        params = {"account_number": request.account_number}
        endpoint = "/orders/"

        if request.start_date is not None:
            if hasattr(request.start_date, "isoformat"):
                params["start_date"] = request.start_date.isoformat()
            else:
                params["start_date"] = request.start_date

        if request.page_size is not None:
            params["page_size"] = request.page_size
        else:
            params["page_size"] = 10

        if self._resolve_symbols:
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
        """Create a cursor that automatically resolves symbols for orders."""

        class SymbolResolvingApiCursor(ApiCursor[StockOrder]):
            def __init__(self, orders_client, *args, **kwargs):
                self._orders_client = orders_client
                super().__init__(*args, **kwargs)

            def _fetch_current_page(self):
                super()._fetch_current_page()
                if (
                    self._current_page
                    and self._current_page.results
                    and hasattr(self._orders_client, "_instrument_client")
                ):
                    for order in self._current_page.results:
                        if not order.symbol:
                            try:
                                symbol = self._orders_client._instrument_client.get_symbol_by_instrument_url(
                                    order.instrument
                                )
                                if symbol:
                                    order.symbol = symbol
                            except Exception:
                                pass

        return SymbolResolvingApiCursor(
            self,
            client=self,
            endpoint=endpoint,
            response_model=StockOrdersPageResponse,
            base_params=base_params,
        )

    # --- Options Orders ---

    def get_options_order(self, request: OptionOrderRequest) -> OptionsOrder:
        """Gets information for a specific options order.

        Args:
            request: An OptionsOrderRequest containing:
                account_number: The Robinhood account number
                order_id: The ID of the order to retrieve

        Returns:
            OptionsOrder with the order information
        """
        params = {}
        endpoint = f"/options/orders/{request.order_id}/"
        if request.account_number is not None:
            params["account_number"] = request.account_number

        res = self.request_get(endpoint, params=params)
        from robinhood_client.common.schema import OptionsOrder

        return OptionsOrder(**res)

    def get_options_orders(
        self, request: OptionOrdersRequest
    ) -> PaginatedResult[OptionsOrder]:
        """Gets a cursor-based paginated result for options orders.

        This method returns a PaginatedResult object that supports both direct access
        to the current page and cursor-based iteration through all pages.

        Args:
            request: An OptionsOrdersRequest containing:
                account_number: The Robinhood account number
                start_date: Optional date filter for orders (accepts string or date object)
                page_size: Optional pagination page size

        Returns:
            PaginatedResult[OptionsOrder] that can be used for:
            - Direct access: result.results, result.next, result.previous
            - Iteration: for order in result: ...
            - Advanced pagination: result.cursor().next(), result.cursor().all()

        Example:
            >>> request = OptionsOrdersRequest(account_number="123")
            >>> result = client.get_options_orders(request)
            >>>
            >>> # Access current page
            >>> current_orders = result.results
            >>>
            >>> # Iterate through all pages
            >>> for order in result:
            >>>     print(f"Order {order.id}: {order.state}")
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
        endpoint = "/options/orders/"

        if request.start_date is not None:
            if hasattr(request.start_date, "isoformat"):
                params["start_date"] = request.start_date.isoformat()
            else:
                params["start_date"] = request.start_date

        if request.page_size is not None:
            params["page_size"] = request.page_size
        else:
            params["page_size"] = 10

        # OptionsOrdersPageResponse already imported above
        cursor = ApiCursor(
            client=self,
            endpoint=endpoint,
            response_model=OptionsOrdersPageResponse,
            base_params=params,
        )

        return PaginatedResult(cursor)
