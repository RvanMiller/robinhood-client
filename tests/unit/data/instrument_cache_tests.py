"""Unit tests for the instrument cache functionality."""

from unittest.mock import Mock, patch
from robinhood_client.data.instruments import InstrumentCacheClient
from robinhood_client.common.session import SessionStorage


class TestInstrumentCacheClient:
    """Test cases for InstrumentCacheClient."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session_storage = Mock(spec=SessionStorage)
        self.client = InstrumentCacheClient(self.mock_session_storage)

    def test_extract_instrument_id_from_url(self):
        """Test extracting instrument ID from URL."""
        # Test valid URL
        url = "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
        instrument_id = self.client._extract_instrument_id_from_url(url)
        assert instrument_id == "e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6"

        # Test URL without trailing slash
        url = "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6"
        instrument_id = self.client._extract_instrument_id_from_url(url)
        assert instrument_id == "e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6"

        # Test invalid URL
        invalid_url = "https://api.robinhood.com/invalid/path/"
        instrument_id = self.client._extract_instrument_id_from_url(invalid_url)
        assert instrument_id is None

    @patch.object(InstrumentCacheClient, 'request_get')
    def test_get_symbol_by_instrument_id_with_cache_miss(self, mock_request_get):
        """Test getting symbol when not in cache."""
        instrument_id = "e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6"
        
        # Mock API response
        mock_response = {
            "id": instrument_id,
            "url": f"https://api.robinhood.com/instruments/{instrument_id}/",
            "symbol": "CRDO",
            "name": "Credo Technology Group Holding Ltd",
            "simple_name": "Credo Technology Group",
            "state": "active",
            "market": "https://api.robinhood.com/markets/XNAS/",
            "tradeable": True,
            "tradability": "tradable",
            "quote": "https://api.robinhood.com/quotes/CRDO/",
            "fundamentals": "https://api.robinhood.com/fundamentals/CRDO/",
            "splits": f"https://api.robinhood.com/instruments/{instrument_id}/splits/",
            "bloomberg_unique": "EQ0000000083917793",
            "margin_initial_ratio": "0.5000",
            "maintenance_ratio": "0.4000",
            "country": "US",
            "day_trade_ratio": "0.2500",
            "list_date": "2022-01-27",
            "min_tick_size": None,
            "type": "stock",
            "tradable_chain_id": "1a09e53e-0858-4c40-9e07-fc14cca74ece",
            "rhs_tradability": "tradable",
            "affiliate_tradability": "tradable",
            "fractional_tradability": "tradable",
            "short_selling_tradability": "tradable",
            "default_collar_fraction": "0.05",
            "ipo_access_status": None,
            "ipo_access_cob_deadline": None,
            "ipo_s1_url": None,
            "ipo_roadshow_url": None,
            "is_spac": False,
            "is_test": False,
            "ipo_access_supports_dsp": False,
            "extended_hours_fractional_tradability": False,
            "internal_halt_reason": "",
            "internal_halt_details": "",
            "internal_halt_sessions": None,
            "internal_halt_start_time": None,
            "internal_halt_end_time": None,
            "internal_halt_source": "",
            "all_day_tradability": "tradable",
            "notional_estimated_quantity_decimals": 5,
            "tax_security_type": "stock",
            "reserved_buying_power_percent_queued": "0.10000000",
            "reserved_buying_power_percent_immediate": "0.05000000",
            "otc_market_tier": "",
            "car_required": False,
            "high_risk_maintenance_ratio": "0.4000",
            "low_risk_maintenance_ratio": "0.2500",
            "default_preset_percent_limit": "0.02"
        }
        mock_request_get.return_value = mock_response

        # Test getting symbol
        symbol = self.client.get_symbol_by_instrument_id(instrument_id)
        
        assert symbol == "CRDO"
        mock_request_get.assert_called_once_with(f"/instruments/{instrument_id}/")
        
        # Verify caching
        assert instrument_id in self.client._symbol_cache
        assert self.client._symbol_cache[instrument_id] == "CRDO"
        assert instrument_id in self.client._instrument_cache

    def test_get_symbol_by_instrument_id_with_cache_hit(self):
        """Test getting symbol when already in cache."""
        instrument_id = "e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6"
        
        # Pre-populate cache
        self.client._symbol_cache[instrument_id] = "CRDO"
        
        # Test getting symbol (should not make API call)
        with patch.object(self.client, 'request_get') as mock_request_get:
            symbol = self.client.get_symbol_by_instrument_id(instrument_id)
            
            assert symbol == "CRDO"
            mock_request_get.assert_not_called()

    @patch.object(InstrumentCacheClient, 'get_symbol_by_instrument_id')
    def test_get_symbol_by_instrument_url(self, mock_get_symbol):
        """Test getting symbol by URL."""
        url = "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
        mock_get_symbol.return_value = "CRDO"
        
        symbol = self.client.get_symbol_by_instrument_url(url)
        
        assert symbol == "CRDO"
        mock_get_symbol.assert_called_once_with("e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6")

    def test_cache_management(self):
        """Test cache clearing and statistics."""
        # Pre-populate caches
        self.client._symbol_cache["test1"] = "SYM1"
        self.client._instrument_cache["test1"] = Mock()
        
        # Test statistics
        stats = self.client.get_cache_stats()
        assert stats["symbol_cache_size"] == 1
        assert stats["instrument_cache_size"] == 1
        
        # Test cache clearing
        self.client.clear_cache()
        stats = self.client.get_cache_stats()
        assert stats["symbol_cache_size"] == 0
        assert stats["instrument_cache_size"] == 0