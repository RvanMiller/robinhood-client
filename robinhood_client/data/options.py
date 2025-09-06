"""Client for retrieving Options data."""

from robinhood_client.common.clients import BaseOAuthClient
from robinhood_client.common.session import SessionStorage
from robinhood_client.common.constants import BASE_API_URL
from robinhood_client.common.schema import OptionsOrder, OptionsOrdersPageResponse
from robinhood_client.common.cursor import ApiCursor, PaginatedResult

from .requests import (
    OptionsOrderRequest,
    OptionsOrdersRequest,
)


class OptionsDataClient(BaseOAuthClient):
    """Client for retrieving Options data."""

    def __init__(self, session_storage: SessionStorage):
        super().__init__(url=BASE_API_URL, session_storage=session_storage)

    def get_options_order(self, request: OptionsOrderRequest) -> OptionsOrder:
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
        return OptionsOrder(**res)

    def get_options_orders(
        self, request: OptionsOrdersRequest
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

        # Create a cursor for this request
        cursor = ApiCursor(
            client=self,
            endpoint=endpoint,
            response_model=OptionsOrdersPageResponse,
            base_params=params,
        )

        return PaginatedResult(cursor)
