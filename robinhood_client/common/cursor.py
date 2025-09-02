"""Cursor pattern implementation for handling paginated API responses."""

from abc import ABC
from typing import Generic, TypeVar, Iterator, Optional, Callable, Any, Dict
from pydantic import BaseModel

from robinhood_client.common.clients import BaseClient

T = TypeVar("T")


class CursorResponse(BaseModel, Generic[T]):
    """Base response model for paginated API responses."""

    results: list[T]
    next: Optional[str] = None
    previous: Optional[str] = None


class Cursor(Generic[T], ABC):
    """Abstract base class for implementing cursor-based pagination."""

    def __init__(
        self,
        fetch_func: Callable[[Optional[str]], CursorResponse[T]],
        initial_cursor: Optional[str] = None,
    ):
        """Initialize the cursor.

        Args:
            fetch_func: Function that takes a cursor URL and returns a CursorResponse
            initial_cursor: Optional initial cursor URL to start from
        """
        self._fetch_func = fetch_func
        self._current_cursor = initial_cursor
        self._current_page: Optional[CursorResponse[T]] = None
        self._has_fetched_first_page = False

    def __iter__(self) -> Iterator[T]:
        """Iterate over all items across all pages."""
        if not self._has_fetched_first_page:
            self._fetch_current_page()

        while self._current_page is not None:
            for item in self._current_page.results:
                yield item

            if not self.has_next():
                break

            self.next()

    def __next__(self) -> T:
        """Get the next item in the iteration."""
        if not hasattr(self, "_iterator"):
            self._iterator = iter(self)
        return next(self._iterator)

    def current_page(self) -> Optional[CursorResponse[T]]:
        """Get the current page of results."""
        if not self._has_fetched_first_page:
            self._fetch_current_page()
        return self._current_page

    def has_next(self) -> bool:
        """Check if there's a next page available."""
        if not self._has_fetched_first_page:
            self._fetch_current_page()
        return self._current_page is not None and self._current_page.next is not None

    def has_previous(self) -> bool:
        """Check if there's a previous page available."""
        if not self._has_fetched_first_page:
            self._fetch_current_page()
        return (
            self._current_page is not None and self._current_page.previous is not None
        )

    def next(self) -> Optional[CursorResponse[T]]:
        """Fetch the next page of results."""
        if not self.has_next():
            return None

        self._current_cursor = self._current_page.next
        self._fetch_current_page()
        return self._current_page

    def previous(self) -> Optional[CursorResponse[T]]:
        """Fetch the previous page of results."""
        if not self.has_previous():
            return None

        self._current_cursor = self._current_page.previous
        self._fetch_current_page()
        return self._current_page

    def reset(self) -> None:
        """Reset the cursor to the beginning."""
        self._current_cursor = None
        self._current_page = None
        self._has_fetched_first_page = False
        if hasattr(self, "_iterator"):
            delattr(self, "_iterator")

    def all(self) -> list[T]:
        """Fetch all items from all pages."""
        items = []
        for item in self:
            items.append(item)
        return items

    def first(self) -> Optional[T]:
        """Get the first item from the first page."""
        if not self._has_fetched_first_page:
            self._fetch_current_page()

        if self._current_page and self._current_page.results:
            return self._current_page.results[0]
        return None

    def _fetch_current_page(self) -> None:
        """Fetch the current page using the fetch function."""
        self._current_page = self._fetch_func(self._current_cursor)
        self._has_fetched_first_page = True


class ApiCursor(Cursor[T]):
    """Concrete implementation of Cursor for API-based pagination."""

    def __init__(
        self,
        client: BaseClient,
        endpoint: str,
        response_model: type[CursorResponse[T]],
        base_params: Optional[Dict[str, Any]] = None,
        initial_cursor: Optional[str] = None,
    ):
        """Initialize the API cursor.

        Args:
            client: The API client instance
            endpoint: The API endpoint path
            response_model: The response model class
            base_params: Base parameters to include in all requests
            initial_cursor: Optional initial cursor URL
        """
        self._client = client
        self._endpoint = endpoint
        self._response_model = response_model
        self._base_params = base_params or {}

        def fetch_func(cursor_url: Optional[str]) -> CursorResponse[T]:
            if cursor_url:
                # If we have a cursor URL, use it directly
                response_data = self._client.request_get(cursor_url)
            else:
                # Otherwise, use the base endpoint with params
                response_data = self._client.request_get(
                    self._endpoint, params=self._base_params
                )

            return self._response_model(**response_data)

        super().__init__(fetch_func, initial_cursor)


class PaginatedResult(Generic[T]):
    """A result object that provides both direct access and cursor-based pagination."""

    def __init__(self, cursor: Cursor[T]):
        """Initialize with a cursor.

        Args:
            cursor: The cursor for pagination
        """
        self._cursor = cursor

    @property
    def results(self) -> list[T]:
        """Get the results from the current page."""
        current_page = self._cursor.current_page()
        return current_page.results if current_page else []

    @property
    def next(self) -> Optional[str]:
        """Get the next page cursor URL."""
        current_page = self._cursor.current_page()
        return current_page.next if current_page else None

    @property
    def previous(self) -> Optional[str]:
        """Get the previous page cursor URL."""
        current_page = self._cursor.current_page()
        return current_page.previous if current_page else None

    def cursor(self) -> Cursor[T]:
        """Get the cursor for advanced pagination operations."""
        return self._cursor

    def __iter__(self) -> Iterator[T]:
        """Iterate over all items across all pages."""
        return iter(self._cursor)

    def __len__(self) -> int:
        """Get the number of items in the current page."""
        return len(self.results)

    def __getitem__(self, index: int) -> T:
        """Get an item from the current page by index."""
        return self.results[index]
