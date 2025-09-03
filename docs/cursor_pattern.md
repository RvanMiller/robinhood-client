# Cursor Pattern Documentation

## Overview

The Robinhood Client uses a Cursor Pattern for handling paginated API responses. This provides a clean and efficient way to work with large datasets that are split across multiple pages.

## Features

- **Cursor-Based Pagination**: The `get_stock_orders()` method returns a `PaginatedResult` object
- **Multiple Usage Patterns**: Direct access, iteration, and manual pagination
- **Efficient**: Only fetches pages as needed (lazy loading)

## Usage Examples

### Method 1: Direct Access (Current Page Only)

```python
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import StockOrdersRequest

# Initialize client and authenticate (see authentication docs)
client = OrdersDataClient(session_storage)
client.login(username, password, mfa_code)

# Create request
request = StockOrdersRequest(account_number="123456", page_size=10)

# Get paginated result
result = client.get_stock_orders(request)

# Access current page
current_orders = result.results  # List[StockOrder]
next_url = result.next          # Optional[str] 
previous_url = result.previous  # Optional[str]
total_count = result.count      # Optional[int]

print(f"Current page has {len(current_orders)} orders")
```

### Method 2: Automatic Iteration (All Pages)

```python
# Iterate through ALL orders across ALL pages automatically
for order in result:
    print(f"Order {order.id}: {order.state} - {order.side} {order.quantity} shares")

# Or collect all orders at once
all_orders = result.cursor().all()
print(f"Total orders: {len(all_orders)}")
```

### Method 3: Manual Pagination Control

```python
cursor = result.cursor()

# Check pagination status
print(f"Has next page: {cursor.has_next()}")
print(f"Has previous page: {cursor.has_previous()}")

# Navigate pages manually
if cursor.has_next():
    next_page = cursor.next()
    print(f"Next page has {len(next_page.results)} orders")

if cursor.has_previous():
    prev_page = cursor.previous()
    print(f"Previous page has {len(prev_page.results)} orders")

# Reset to first page
cursor.reset()
```

### Method 4: Page-by-Page Processing

```python
cursor = result.cursor()
page_number = 1

# Process each page individually
while True:
    current_page = cursor.current_page()
    print(f"Processing page {page_number} ({len(current_page.results)} orders)")
    
    for order in current_page.results:
        # Process each order
        process_order(order)
    
    if not cursor.has_next():
        break
    
    cursor.next()
    page_number += 1
```

## API Reference

### PaginatedResult[T]

The main interface for working with paginated results.

#### Properties:
- `results: List[T]` - Items from the current page
- `next: Optional[str]` - URL for the next page (if available)
- `previous: Optional[str]` - URL for the previous page (if available)  
- `count: Optional[int]` - Total count of items (if provided by API)

#### Methods:
- `cursor() -> Cursor[T]` - Get the underlying cursor for advanced operations
- `__iter__()` - Iterate over all items across all pages
- `__len__()` - Get count of items in current page
- `__getitem__(index)` - Get item from current page by index

### Cursor[T]

Advanced cursor interface for pagination control.

#### Methods:
- `current_page() -> Optional[CursorResponse[T]]` - Get current page
- `has_next() -> bool` - Check if next page exists
- `has_previous() -> bool` - Check if previous page exists
- `next() -> Optional[CursorResponse[T]]` - Fetch next page
- `previous() -> Optional[CursorResponse[T]]` - Fetch previous page
- `reset() -> None` - Reset cursor to beginning
- `all() -> List[T]` - Fetch all items from all pages
- `first() -> Optional[T]` - Get first item from first page
- `__iter__()` - Iterate over all items across all pages

## Performance Considerations

- **Lazy Loading**: Pages are only fetched when accessed
- **Memory Efficient**: Only current page is kept in memory during iteration
- **Flexible**: Choose between processing one page at a time or loading all data
- **Network Efficient**: Automatic iteration stops when no more pages are available

## Migration Guide

### Existing Code (Still Works)
```python
# This continues to work unchanged
orders_response = client.get_stock_orders(request)
for order in orders_response.results:
    process_order(order)

# Manual pagination with traditional approach
next_url = orders_response.next
if next_url:
    # Would need to manually construct next request...
```

### Cursor Approach
```python
# Clean cursor pattern
result = client.get_stock_orders(request)

# Automatic pagination
for order in result:
    process_order(order)

# Or manual pagination  
cursor = result.cursor()
while cursor.has_next():
    page = cursor.next()
    for order in page.results:
        process_order(order)
```

## Error Handling

The cursor pattern handles errors gracefully:

```python
try:
    result = client.get_stock_orders(request)
    for order in result:
        process_order(order)
except Exception as e:
    print(f"Error fetching orders: {e}")
```

If a network error occurs while iterating, the exception will be raised at that point, allowing you to handle it appropriately.
