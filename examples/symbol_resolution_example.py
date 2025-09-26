"""Example demonstrating symbol resolution for stock orders."""

from robinhood_client.data import OrdersDataClient, StockOrdersRequest
from robinhood_client.common.session import FileSystemSessionStorage


def main():
    """Demonstrate symbol resolution functionality."""
    # Initialize the client with session storage
    session_storage = FileSystemSessionStorage()
    orders_client = OrdersDataClient(session_storage)

    # Example 1: Get orders with symbol resolution enabled (default)
    print("=== Example 1: Orders with symbol resolution (default) ===")
    request = StockOrdersRequest(account_number="your_account_number")
    orders_result = orders_client.get_stock_orders(request)

    for order in orders_result:
        print(f"Order ID: {order.id}")
        print(f"Symbol: {order.symbol}")  # This will be populated
        print(f"State: {order.state}")
        print(f"Side: {order.side}")
        print(f"Quantity: {order.quantity}")
        print("---")

    # Example 2: Get orders without symbol resolution
    print("=== Example 2: Orders without symbol resolution ===")
    request_no_symbols = StockOrdersRequest(
        account_number="your_account_number", resolve_symbols=False
    )
    orders_result_no_symbols = orders_client.get_stock_orders(request_no_symbols)

    for order in orders_result_no_symbols:
        print(f"Order ID: {order.id}")
        print(f"Symbol: {order.symbol}")  # This will be None
        print(f"Instrument URL: {order.instrument}")  # Raw instrument URL
        print(f"State: {order.state}")
        print("---")

    # Example 3: Manual symbol resolution using instrument client
    print("=== Example 3: Manual symbol resolution ===")
    # Access the underlying instrument client
    instrument_client = orders_client._instrument_client

    # Resolve symbol from instrument URL
    example_url = (
        "https://api.robinhood.com/instruments/e84dc27d-7b8e-4f21-b3bd-5b02a5c99bc6/"
    )
    symbol = instrument_client.get_symbol_by_instrument_url(example_url)
    print(f"Symbol for instrument URL: {symbol}")  # Should print "CRDO"

    # Check cache stats
    cache_stats = instrument_client.get_cache_stats()
    print(f"Cache statistics: {cache_stats}")


if __name__ == "__main__":
    main()
