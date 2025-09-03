"""Example demonstrating the Cursor Pattern usage."""

from robinhood_client.common.session import FileSystemSessionStorage
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.requests import StockOrdersRequest


def example_traditional_pagination():
    """Example using the traditional pagination approach."""
    print("=== Traditional Pagination Example ===")

    session_storage = FileSystemSessionStorage()
    client = OrdersDataClient(session_storage=session_storage)
    client.login()
    account_number = "123ABC"

    request = StockOrdersRequest(account_number=account_number, page_size=5)

    # Traditional approach - get one page at a time
    orders_response = client.get_stock_orders(request)
    print(f"Current page has {len(orders_response.results)} orders")
    print(f"Next page URL: {orders_response.next}")
    print(f"Previous page URL: {orders_response.previous}")

    # Process current page
    for order in orders_response.results:
        print(f"  Order {order.id}: {order.state} - {order.side} {order.quantity}")


def example_cursor_pagination():
    """Example using cursor-based pagination."""
    print("\n=== Cursor Pattern Example ===")

    session_storage = FileSystemSessionStorage()
    client = OrdersDataClient(session_storage=session_storage)
    client.login()
    account_number = "123ABC"

    request = StockOrdersRequest(account_number=account_number, page_size=5)

    # Cursor approach
    response = client.get_stock_orders(request)

    print("--- Method 1: Direct access to current page ---")
    print(f"Current page has {len(response.results)} orders")
    print(f"Has next page: {response.cursor().has_next()}")

    # Process current page only
    for order in response.results:
        print(f"  Order {order.id}: {order.state} - {order.side} {order.quantity}")

    print("\n--- Method 2: Iterate through ALL pages automatically ---")
    order_count = 0
    for order in response:
        order_count += 1
        print(f"  Order {order_count}: {order.id} - {order.state}")
        if order_count >= 10:  # Limit output for example
            print("  ... (limiting output for example)")
            break

    print("\n--- Method 3: Manual pagination control ---")
    cursor = response.cursor()
    cursor.reset()  # Reset to beginning

    page_num = 1
    while True:
        current_page = cursor.current_page()
        print(f"Page {page_num}: {len(current_page.results)} orders")

        for order in current_page.results:
            print(f"  {order.id}: {order.state}")

        if not cursor.has_next():
            break

        cursor.next()
        page_num += 1

        if page_num > 3:  # Limit for example
            print("  ... (limiting pages for example)")
            break

    print("\n--- Method 4: Get all orders at once ---")
    cursor.reset()
    all_orders = cursor.all()
    print(f"Total orders retrieved: {len(all_orders)}")

    print("(Commented out - add credentials to test)")


def example_error_handling():
    """Example showing error handling with cursor pattern."""
    print("\n=== Error Handling Example ===")

    session_storage = FileSystemSessionStorage()
    client = OrdersDataClient(session_storage=session_storage)

    # Example without authentication (will fail)
    request = StockOrdersRequest(account_number="123456", page_size=5)

    try:
        result = client.get_stock_orders(request)
        # This would trigger the first API call
        result.cursor().current_page()
        print("Successfully fetched orders")
    except Exception as e:
        print(f"Expected error (not authenticated): {type(e).__name__}")


def main():
    """Run all examples."""
    print("Robinhood Client - Cursor Pattern Examples")
    print("=" * 50)

    example_traditional_pagination()
    example_cursor_pagination()
    example_error_handling()

    print("\n" + "=" * 50)
    print("Examples complete!")


if __name__ == "__main__":
    main()
