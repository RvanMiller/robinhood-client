"""Client for fetching and caching instrument data."""

import logging
from typing import Dict, Optional
from urllib.parse import urlparse

from robinhood_client.common.clients import BaseOAuthClient
from robinhood_client.common.session import SessionStorage
from robinhood_client.common.constants import BASE_API_URL
from robinhood_client.common.schema import Instrument

logger = logging.getLogger(__name__)


class InstrumentCacheClient(BaseOAuthClient):
    """Client for fetching and caching instrument data with symbol lookup functionality.

    This client provides caching capabilities to avoid repeated API calls for the same
    instruments. It's designed to be used by other data clients to resolve symbols
    from instrument URLs or IDs.
    """

    def __init__(self, session_storage: SessionStorage):
        """Initialize the instrument cache client.

        Args:
            session_storage: Session storage for authentication
        """
        super().__init__(url=BASE_API_URL, session_storage=session_storage)
        self._symbol_cache: Dict[str, str] = {}  # instrument_id -> symbol
        self._instrument_cache: Dict[
            str, Instrument
        ] = {}  # instrument_id -> full instrument

    def get_symbol_by_instrument_id(self, instrument_id: str) -> Optional[str]:
        """Get the trading symbol for an instrument by its ID.

        This method first checks the cache, and if not found, fetches the instrument
        from the API and caches both the symbol and full instrument data.

        Args:
            instrument_id: The unique identifier for the instrument

        Returns:
            The trading symbol (e.g., 'CRDO') or None if not found
        """
        # Check symbol cache first
        if instrument_id in self._symbol_cache:
            logger.debug(f"Symbol cache hit for instrument_id: {instrument_id}")
            return self._symbol_cache[instrument_id]

        # Fetch and cache the instrument
        instrument = self._fetch_and_cache_instrument(instrument_id)
        return instrument.symbol if instrument else None

    def get_symbol_by_instrument_url(self, instrument_url: str) -> Optional[str]:
        """Get the trading symbol for an instrument by its URL.

        Extracts the instrument ID from the URL and uses get_symbol_by_instrument_id.

        Args:
            instrument_url: The URL for the instrument (e.g., 'https://api.robinhood.com/instruments/abc123/')

        Returns:
            The trading symbol (e.g., 'CRDO') or None if not found
        """
        instrument_id = self._extract_instrument_id_from_url(instrument_url)
        if not instrument_id:
            logger.warning(
                f"Could not extract instrument ID from URL: {instrument_url}"
            )
            return None

        return self.get_symbol_by_instrument_id(instrument_id)

    def get_instrument_by_id(self, instrument_id: str) -> Optional[Instrument]:
        """Get the full instrument data by its ID.

        This method first checks the cache, and if not found, fetches the instrument
        from the API and caches it.

        Args:
            instrument_id: The unique identifier for the instrument

        Returns:
            The full Instrument object or None if not found
        """
        # Check instrument cache first
        if instrument_id in self._instrument_cache:
            logger.debug(f"Instrument cache hit for instrument_id: {instrument_id}")
            return self._instrument_cache[instrument_id]

        # Fetch and cache the instrument
        return self._fetch_and_cache_instrument(instrument_id)

    def clear_cache(self) -> None:
        """Clear both symbol and instrument caches."""
        self._symbol_cache.clear()
        self._instrument_cache.clear()
        logger.info("Instrument cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """Get statistics about the cache.

        Returns:
            Dictionary with cache statistics including sizes
        """
        return {
            "symbol_cache_size": len(self._symbol_cache),
            "instrument_cache_size": len(self._instrument_cache),
        }

    def _fetch_and_cache_instrument(self, instrument_id: str) -> Optional[Instrument]:
        """Fetch instrument data from API and cache it.

        Args:
            instrument_id: The unique identifier for the instrument

        Returns:
            The Instrument object or None if not found/error occurred
        """
        try:
            endpoint = f"/instruments/{instrument_id}/"
            logger.debug(f"Fetching instrument data for ID: {instrument_id}")

            response = self.request_get(endpoint)
            instrument = Instrument(**response)

            # Cache both the symbol and full instrument
            self._symbol_cache[instrument_id] = instrument.symbol
            self._instrument_cache[instrument_id] = instrument

            logger.debug(
                f"Cached instrument {instrument_id} with symbol: {instrument.symbol}"
            )
            return instrument

        except Exception as e:
            logger.error(f"Failed to fetch instrument {instrument_id}: {e}")
            return None

    def _extract_instrument_id_from_url(self, instrument_url: str) -> Optional[str]:
        """Extract instrument ID from a Robinhood instrument URL.

        Args:
            instrument_url: The URL (e.g., 'https://api.robinhood.com/instruments/abc123/')

        Returns:
            The instrument ID or None if extraction fails
        """
        try:
            # Parse the URL and extract the path
            parsed_url = urlparse(instrument_url)
            path_parts = parsed_url.path.strip("/").split("/")

            # Expected format: /instruments/{instrument_id}/
            if len(path_parts) >= 2 and path_parts[0] == "instruments":
                return path_parts[1]

            logger.warning(f"Unexpected URL format: {instrument_url}")
            return None

        except Exception as e:
            logger.error(
                f"Error extracting instrument ID from URL {instrument_url}: {e}"
            )
            return None
