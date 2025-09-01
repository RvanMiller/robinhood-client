"""Unit tests for the Cursor Pattern implementation."""

from unittest.mock import Mock
from robinhood_client.common.cursor import Cursor, ApiCursor, PaginatedResult, CursorResponse
from robinhood_client.common.schema import StockOrder, StockOrdersPageResponse


class TestCursor:
    """Test the base Cursor class."""

    def test_cursor_initialization(self):
        """Test cursor can be initialized with a fetch function."""
        fetch_func = Mock()
        cursor = Cursor(fetch_func)
        
        assert cursor._fetch_func == fetch_func
        assert cursor._current_cursor is None
        assert cursor._current_page is None
        assert cursor._has_fetched_first_page is False

    def test_cursor_current_page_fetches_first_page(self):
        """Test that accessing current_page fetches the first page."""
        mock_response = CursorResponse(results=[{"id": "1"}], next="next_url", previous=None)
        fetch_func = Mock(return_value=mock_response)
        
        cursor = Cursor(fetch_func)
        current_page = cursor.current_page()
        
        assert current_page == mock_response
        assert cursor._has_fetched_first_page is True
        fetch_func.assert_called_once_with(None)

    def test_cursor_has_next_true(self):
        """Test has_next returns True when next URL exists."""
        mock_response = CursorResponse(results=[{"id": "1"}], next="next_url", previous=None)
        fetch_func = Mock(return_value=mock_response)
        
        cursor = Cursor(fetch_func)
        
        assert cursor.has_next() is True

    def test_cursor_has_next_false(self):
        """Test has_next returns False when next URL is None."""
        mock_response = CursorResponse(results=[{"id": "1"}], next=None, previous=None)
        fetch_func = Mock(return_value=mock_response)
        
        cursor = Cursor(fetch_func)
        
        assert cursor.has_next() is False

    def test_cursor_next_page(self):
        """Test fetching next page."""
        first_page = CursorResponse(results=[{"id": "1"}], next="next_url", previous=None)
        second_page = CursorResponse(results=[{"id": "2"}], next=None, previous="prev_url")
        
        fetch_func = Mock(side_effect=[first_page, second_page])
        
        cursor = Cursor(fetch_func)
        
        # Access first page
        cursor.current_page()
        
        # Move to next page
        next_page = cursor.next()
        
        assert next_page == second_page
        assert cursor._current_cursor == "next_url"
        assert fetch_func.call_count == 2

    def test_cursor_iteration(self):
        """Test iterating through all items across pages."""
        page1 = CursorResponse(results=["item1", "item2"], next="next_url", previous=None)
        page2 = CursorResponse(results=["item3", "item4"], next=None, previous="prev_url")
        
        fetch_func = Mock(side_effect=[page1, page2])
        
        cursor = Cursor(fetch_func)
        items = list(cursor)
        
        assert items == ["item1", "item2", "item3", "item4"]
        assert fetch_func.call_count == 2

    def test_cursor_all(self):
        """Test getting all items at once."""
        page1 = CursorResponse(results=["item1", "item2"], next="next_url", previous=None)
        page2 = CursorResponse(results=["item3", "item4"], next=None, previous="prev_url")
        
        fetch_func = Mock(side_effect=[page1, page2])
        
        cursor = Cursor(fetch_func)
        all_items = cursor.all()
        
        assert all_items == ["item1", "item2", "item3", "item4"]

    def test_cursor_first(self):
        """Test getting the first item."""
        mock_response = CursorResponse(results=["item1", "item2"], next=None, previous=None)
        fetch_func = Mock(return_value=mock_response)
        
        cursor = Cursor(fetch_func)
        first_item = cursor.first()
        
        assert first_item == "item1"

    def test_cursor_reset(self):
        """Test resetting the cursor."""
        mock_response = CursorResponse(results=["item1"], next=None, previous=None)
        fetch_func = Mock(return_value=mock_response)
        
        cursor = Cursor(fetch_func)
        cursor.current_page()  # Trigger first fetch
        
        cursor.reset()
        
        assert cursor._current_cursor is None
        assert cursor._current_page is None
        assert cursor._has_fetched_first_page is False


class TestApiCursor:
    """Test the ApiCursor implementation."""

    def test_api_cursor_initialization(self):
        """Test ApiCursor can be initialized with client and endpoint."""
        mock_client = Mock()
        cursor = ApiCursor(
            client=mock_client,
            endpoint="/test/",
            response_model=CursorResponse,
            base_params={"param1": "value1"}
        )
        
        assert cursor._client == mock_client
        assert cursor._endpoint == "/test/"
        assert cursor._response_model == CursorResponse
        assert cursor._base_params == {"param1": "value1"}

    def test_api_cursor_fetch_with_endpoint(self):
        """Test ApiCursor makes correct API call when no cursor URL provided."""
        mock_client = Mock()
        mock_client.request_get.return_value = {"results": [], "next": None, "previous": None}
        
        cursor = ApiCursor(
            client=mock_client,
            endpoint="/test/",
            response_model=CursorResponse,
            base_params={"param1": "value1"}
        )
        
        cursor.current_page()
        
        mock_client.request_get.assert_called_once_with("/test/", params={"param1": "value1"})

    def test_api_cursor_fetch_with_cursor_url(self):
        """Test ApiCursor makes correct API call when cursor URL provided."""
        mock_response1 = {"results": ["item1"], "next": "http://api.example.com/test/?cursor=abc", "previous": None}
        mock_response2 = {"results": ["item2"], "next": None, "previous": "http://api.example.com/test/?cursor=def"}
        
        mock_client = Mock()
        mock_client.request_get.side_effect = [mock_response1, mock_response2]
        
        cursor = ApiCursor(
            client=mock_client,
            endpoint="/test/",
            response_model=CursorResponse,
            base_params={"param1": "value1"}
        )
        
        # Get first page
        cursor.current_page()
        # Get second page
        cursor.next()
        
        # Check both calls
        assert mock_client.request_get.call_count == 2
        mock_client.request_get.assert_any_call("/test/", params={"param1": "value1"})
        mock_client.request_get.assert_any_call("http://api.example.com/test/?cursor=abc")


class TestPaginatedResult:
    """Test the PaginatedResult wrapper."""

    def test_paginated_result_initialization(self):
        """Test PaginatedResult can be initialized with a cursor."""
        mock_cursor = Mock()
        result = PaginatedResult(mock_cursor)
        
        assert result._cursor == mock_cursor

    def test_paginated_result_results_property(self):
        """Test results property returns current page results."""
        mock_page = CursorResponse(results=["item1", "item2"], next=None, previous=None)
        mock_cursor = Mock()
        mock_cursor.current_page.return_value = mock_page
        
        result = PaginatedResult(mock_cursor)
        
        assert result.results == ["item1", "item2"]

    def test_paginated_result_next_property(self):
        """Test next property returns next URL."""
        mock_page = CursorResponse(results=[], next="next_url", previous=None)
        mock_cursor = Mock()
        mock_cursor.current_page.return_value = mock_page
        
        result = PaginatedResult(mock_cursor)
        
        assert result.next == "next_url"

    def test_paginated_result_iteration(self):
        """Test PaginatedResult can be iterated."""
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter(["item1", "item2"]))
        
        result = PaginatedResult(mock_cursor)
        items = list(result)
        
        assert items == ["item1", "item2"]

    def test_paginated_result_len(self):
        """Test len() returns current page length."""
        mock_page = CursorResponse(results=["item1", "item2"], next=None, previous=None)
        mock_cursor = Mock()
        mock_cursor.current_page.return_value = mock_page
        
        result = PaginatedResult(mock_cursor)
        
        assert len(result) == 2

    def test_paginated_result_getitem(self):
        """Test indexing returns item from current page."""
        mock_page = CursorResponse(results=["item1", "item2"], next=None, previous=None)
        mock_cursor = Mock()
        mock_cursor.current_page.return_value = mock_page
        
        result = PaginatedResult(mock_cursor)
        
        assert result[0] == "item1"
        assert result[1] == "item2"


class TestStockOrdersIntegration:
    """Integration test for StockOrders with cursor pattern."""

    def create_mock_stock_order(self, order_id: str) -> dict:
        """Create a mock stock order dictionary."""
        return {
            "id": order_id,
            "ref_id": f"ref_{order_id}",
            "url": f"https://api.robinhood.com/orders/{order_id}/",
            "account": "https://api.robinhood.com/accounts/123/",
            "user_uuid": "user-uuid",
            "position": f"https://api.robinhood.com/positions/123/{order_id}/",
            "cancel": None,
            "instrument": "https://api.robinhood.com/instruments/abc123/",
            "instrument_id": "abc123",
            "cumulative_quantity": "10.0000",
            "average_price": "150.00",
            "fees": "0.00",
            "sec_fees": "0.00",
            "taf_fees": "0.00",
            "cat_fees": "0.00",
            "sales_taxes": [],
            "state": "filled",
            "derived_state": "filled",
            "pending_cancel_open_agent": None,
            "type": "market",
            "side": "buy",
            "time_in_force": "gfd",
            "trigger": "immediate",
            "price": None,
            "stop_price": None,
            "quantity": "10.0000",
            "reject_reason": None,
            "created_at": "2023-01-01T10:00:00Z",
            "updated_at": "2023-01-01T10:00:00Z",
            "last_transaction_at": "2023-01-01T10:00:00Z",
            "executions": [],
            "extended_hours": False,
            "market_hours": "regular_hours",
            "override_dtbp_checks": False,
            "override_day_trade_checks": False,
            "response_category": None,
            "stop_triggered_at": None,
            "last_trail_price": None,
            "last_trail_price_updated_at": None,
            "last_trail_price_source": None,
            "dollar_based_amount": None,
            "total_notional": None,
            "executed_notional": None,
            "investment_schedule_id": None,
            "is_ipo_access_order": False,
            "ipo_access_cancellation_reason": None,
            "ipo_access_lower_collared_price": None,
            "ipo_access_upper_collared_price": None,
            "ipo_access_upper_price": None,
            "ipo_access_lower_price": None,
            "is_ipo_access_price_finalized": False,
            "is_visible_to_user": True,
            "has_ipo_access_custom_price_limit": False,
            "is_primary_account": True,
            "order_form_version": 6,
            "preset_percent_limit": None,
            "order_form_type": "share_based_market_buys",
            "last_update_version": 2,
            "placed_agent": "user",
            "is_editable": False,
            "replaces": None,
            "user_cancel_request_state": "order_finalized",
            "tax_lot_selection_type": None,
            "position_effect": "open"
        }

    def test_stock_orders_page_response_creation(self):
        """Test that StockOrdersPageResponse can be created with mock data."""
        mock_order_data = self.create_mock_stock_order("order1")
        
        response_data = {
            "results": [mock_order_data],
            "next": "https://api.robinhood.com/orders/?cursor=next",
            "previous": None,
            "count": 100
        }
        
        response = StockOrdersPageResponse(**response_data)
        
        assert len(response.results) == 1
        assert isinstance(response.results[0], StockOrder)
        assert response.results[0].id == "order1"
        assert response.next == "https://api.robinhood.com/orders/?cursor=next"
        assert response.count == 100
