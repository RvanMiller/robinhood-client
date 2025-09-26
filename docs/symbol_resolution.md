# Symbol Resolution Feature

This document describes the new symbol resolution feature that allows stock orders to include the trading symbol in addition to the instrument URL and ID.

## Overview

Previously, the Orders data client only returned Robinhood's internal instrument URL and instrument ID. Now, the client can optionally resolve these to actual trading symbols (e.g., "CRDO", "AAPL") by making additional API calls to fetch instrument details.

## Features

### Automatic Symbol Resolution

By default, all stock orders now include the resolved trading symbol:

```python
from robinhood_client.data import OrdersDataClient, StockOrdersRequest
from robinhood_client.common.session import FileSystemSessionStorage

# Initialize client
session_storage = FileSystemSessionStorage()
client = OrdersDataClient(session_storage)

# Get orders with automatic symbol resolution
request = StockOrdersRequest(account_number="your_account")
orders = client.get_stock_orders(request)

for order in orders:
    print(f"Order: {order.symbol} ({order.state})")  # e.g., "Order: CRDO (filled)"
```

### Configurable Resolution

Symbol resolution can be disabled for better performance when symbols aren't needed:

```python
# Disable symbol resolution
request = StockOrdersRequest(
    account_number="your_account",
    resolve_symbols=False
)
orders = client.get_stock_orders(request)

for order in orders:
    print(f"Instrument: {order.instrument}")  # Raw instrument URL
    print(f"Symbol: {order.symbol}")  # Will be None
```

### Intelligent Caching

The symbol resolution uses an intelligent caching system to minimize API calls:

```python
# Access the instrument cache directly
instrument_client = client._instrument_client

# Get cache statistics
stats = instrument_client.get_cache_stats()
print(f"Cached symbols: {stats['symbol_cache_size']}")

# Clear cache if needed
instrument_client.clear_cache()
```

## API Reference

### StockOrder Schema Changes

The `StockOrder` model now includes an optional `symbol` field:

```python
class StockOrder(RobinhoodBaseModel):
    # ... existing fields ...
    
    symbol: Optional[str] = None
    """The trading symbol for the stock (populated when symbol resolution is enabled)."""
```

### Request Model Changes

Both `StockOrderRequest` and `StockOrdersRequest` now support a `resolve_symbols` parameter:

```python
class StockOrdersRequest(RobinhoodBaseModel):
    account_number: str
    start_date: Optional[date | str] = None
    page_size: Optional[int] = 10
    resolve_symbols: bool = True  # New parameter, defaults to True
```

### New InstrumentCacheClient

A new client is available for advanced instrument data operations:

```python
from robinhood_client.data import InstrumentCacheClient

client = InstrumentCacheClient(session_storage)

# Get symbol by instrument ID
symbol = client.get_symbol_by_instrument_id("e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6")

# Get symbol by instrument URL
symbol = client.get_symbol_by_instrument_url(
    "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
)

# Get full instrument data
instrument = client.get_instrument_by_id("e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6")
```

## Performance Considerations

### Caching Strategy

- **Symbol Cache**: Stores instrument_id -> symbol mappings
- **Instrument Cache**: Stores full instrument objects for potential future use
- **Automatic Cleanup**: No automatic cleanup implemented; use `clear_cache()` if memory is a concern

### API Call Optimization

- Only unique instruments per page trigger new API calls
- Subsequent requests for the same instruments use cached data
- Pagination respects caching across different pages

### When to Disable Resolution

Consider disabling symbol resolution when:

- Processing large numbers of orders where symbols aren't needed
- Implementing high-frequency operations where latency matters
- Working with orders programmatically where instrument IDs are sufficient

## Backwards Compatibility

This feature is fully backwards compatible:

- Existing code continues to work without changes
- Symbol resolution is enabled by default
- The `symbol` field is optional and won't break existing deserialization
- All existing fields and functionality remain unchanged

## Options Orders

Currently, symbol resolution is only implemented for stock orders. Options orders already include a `chain_symbol` field that provides the underlying symbol. Future releases may extend this functionality to options if needed.

## Error Handling

The symbol resolution is designed to be fault-tolerant:

- Network errors during symbol lookup don't fail the main order request
- Invalid or missing instrument data results in `None` symbol values
- Cache errors are logged but don't interrupt normal operation
- Failed symbol resolution doesn't prevent order data from being returned

## Example Usage

### Basic Usage

```python
from robinhood_client.data import OrdersDataClient, StockOrdersRequest
from robinhood_client.common.session import FileSystemSessionStorage

# Setup
session_storage = FileSystemSessionStorage()
client = OrdersDataClient(session_storage)

# Get recent orders with symbols
request = StockOrdersRequest(account_number="your_account_number")
result = client.get_stock_orders(request)

# Process orders
for order in result:
    if order.symbol:
        print(f"{order.symbol}: {order.state} - {order.side} {order.quantity}")
    else:
        print(f"Unknown symbol: {order.state} - {order.side} {order.quantity}")
```

### Performance-Optimized Usage

```python
# For high-volume processing, disable symbol resolution
request = StockOrdersRequest(
    account_number="your_account_number", 
    resolve_symbols=False,
    page_size=100  # Larger page size for fewer API calls
)

result = client.get_stock_orders(request)

# Process using instrument IDs instead of symbols
for order in result:
    print(f"Instrument ID: {order.instrument_id}, State: {order.state}")
```

### Manual Symbol Resolution

```python
# Get orders without automatic resolution
request = StockOrdersRequest(
    account_number="your_account_number",
    resolve_symbols=False
)
result = client.get_stock_orders(request)

# Manually resolve symbols for specific orders
instrument_client = client._instrument_client

for order in result:
    if order.state == "filled":  # Only resolve for filled orders
        symbol = instrument_client.get_symbol_by_instrument_url(order.instrument)
        print(f"Filled order: {symbol}")
```