"""
Example demonstrating how to use the OptionsDataClient for retrieving options order data.

This example shows:
- Basic options order retrieval
- Pagination with cursor support  
- Date filtering
- Working with options-specific data like legs, chains, and premiums

Requirements:
- Set environment variables: RH_USERNAME, RH_PASSWORD, RH_MFA_CODE
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import pyotp

from robinhood_client.common.session import FileSystemSessionStorage
from robinhood_client.data.options import OptionsDataClient


def create_authenticated_client() -> Optional[OptionsDataClient]:
    """Create and authenticate an OptionsDataClient."""
    # Check for required environment variables
    username = os.environ.get("RH_USERNAME")
    password = os.environ.get("RH_PASSWORD")
    mfa_code = os.environ.get("RH_MFA_CODE")
    
    if not all([username, password, mfa_code]):
        print("Required environment variables not set:")
        print("- RH_USERNAME: Your Robinhood username")
        print("- RH_PASSWORD: Your Robinhood password")
        print("- RH_MFA_CODE: Your MFA code")
        return None
    
    # Create session storage and client
    session_storage = FileSystemSessionStorage()
    client = OptionsDataClient(session_storage=session_storage)
    
    try:
        # Generate TOTP code and authenticate
        totp = pyotp.TOTP(mfa_code).now()
        client.login(username=username, password=password, mfa_code=totp)
        print("✓ Successfully authenticated with Robinhood")
        return client
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None


def demonstrate_basic_options_retrieval(client: OptionsDataClient) -> None:
    """Demonstrate basic options order retrieval."""
    print("\n" + "="*60)
    print("BASIC OPTIONS ORDER RETRIEVAL")
    print("="*60)
    
    try:
        # Get first page of options orders
        result = client.get_options_orders()
        
        print(f"Total orders found: {len(result.results)}")
        print(f"Has more pages: {result.cursor.has_next()}")
        
        if result.results:
            order = result.results[0]
            print("\nFirst order details:")
            print(f"  ID: {order.id}")
            print(f"  Chain Symbol: {order.chain_symbol}")
            print(f"  State: {order.state}")
            print(f"  Strategy: {order.strategy}")
            print(f"  Premium: ${order.premium}")
            print(f"  Number of legs: {len(order.legs)}")
            
            # Show leg details
            for i, leg in enumerate(order.legs):
                print(f"  Leg {i+1}:")
                print(f"    Side: {leg.side}")
                print(f"    Position Effect: {leg.position_effect}")
                print(f"    Quantity: {leg.quantity}")
                if leg.executions:
                    print(f"    Executions: {len(leg.executions)}")
                    
    except Exception as e:
        print(f"❌ Error retrieving options orders: {e}")


def demonstrate_cursor_pagination(client: OptionsDataClient) -> None:
    """Demonstrate cursor-based pagination."""
    print("\n" + "="*60)
    print("CURSOR PAGINATION EXAMPLE")
    print("="*60)
    
    try:
        result = client.get_options_orders(page_size=5)  # Small page size for demo
        order_count = 0
        page_count = 0
        
        # Iterate through all pages
        for order in result.cursor:
            order_count += 1
            if order_count == 1:  # New page started
                page_count += 1
                print(f"\nPage {page_count}:")
            
            print(f"  {order_count:2d}. {order.chain_symbol} - {order.state} - ${order.premium}")
            
            # Limit demo to first 15 orders
            if order_count >= 15:
                break
                
        print(f"\nProcessed {order_count} orders across {page_count} pages")
        
    except Exception as e:
        print(f"❌ Error during pagination: {e}")


def demonstrate_date_filtering(client: OptionsDataClient) -> None:
    """Demonstrate filtering options orders by date."""
    print("\n" + "="*60)
    print("DATE FILTERING EXAMPLE")
    print("="*60)
    
    try:
        # Get orders from the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        date_string = thirty_days_ago.strftime('%Y-%m-%d')
        
        result = client.get_options_orders(updated_at=date_string)
        print(f"Orders updated since {date_string}: {len(result.results)}")
        
        if result.results:
            print("\nRecent orders:")
            for i, order in enumerate(result.results[:5]):  # Show first 5
                print(f"  {i+1}. {order.chain_symbol} - {order.updated_at}")
                
    except Exception as e:
        print(f"❌ Error filtering by date: {e}")


def demonstrate_specific_order_retrieval(client: OptionsDataClient) -> None:
    """Demonstrate retrieving a specific options order."""
    print("\n" + "="*60)
    print("SPECIFIC ORDER RETRIEVAL")
    print("="*60)
    
    try:
        # First get an order ID
        result = client.get_options_orders(page_size=1)
        if not result.results:
            print("No orders found to demonstrate with")
            return
            
        order_id = result.results[0].id
        print(f"Retrieving specific order: {order_id}")
        
        # Get the specific order
        specific_order = client.get_options_order(order_id)
        
        print("\nOrder Details:")
        print(f"  ID: {specific_order.id}")
        print(f"  Ref ID: {specific_order.ref_id}")
        print(f"  Chain Symbol: {specific_order.chain_symbol}")
        print(f"  Strategy: {specific_order.strategy}")
        print(f"  State: {specific_order.state}")
        print(f"  Premium: ${specific_order.premium}")
        print(f"  Direction: {specific_order.direction}")
        print(f"  Time in Force: {specific_order.time_in_force}")
        
        print("\nLeg Details:")
        for i, leg in enumerate(specific_order.legs):
            print(f"  Leg {i+1}:")
            print(f"    Side: {leg.side}")
            print(f"    Position Effect: {leg.position_effect}")
            print(f"    Quantity: {leg.quantity}")
            print(f"    Ratio Quantity: {leg.ratio_quantity}")
            
            if leg.executions:
                print(f"    Executions ({len(leg.executions)}):")
                for j, execution in enumerate(leg.executions):
                    print(f"      {j+1}. Price: ${execution.price}, Quantity: {execution.quantity}")
                    print(f"         Time: {execution.timestamp}")
                    
    except Exception as e:
        print(f"❌ Error retrieving specific order: {e}")


def main():
    """Main example function."""
    print("Robinhood Options Data Client Example")
    print("====================================")
    
    # Create authenticated client
    client = create_authenticated_client()
    if not client:
        return
    
    # Run demonstrations
    demonstrate_basic_options_retrieval(client)
    demonstrate_cursor_pagination(client)
    demonstrate_date_filtering(client)
    demonstrate_specific_order_retrieval(client)
    
    print("\n" + "="*60)
    print("EXAMPLE COMPLETE")
    print("="*60)
    print("\nKey Features Demonstrated:")
    print("✓ Authentication with MFA")
    print("✓ Basic options order retrieval")
    print("✓ Cursor-based pagination")
    print("✓ Date filtering")
    print("✓ Specific order retrieval")
    print("✓ Working with options legs and executions")
    print("✓ Options-specific fields (chain, premium, strategy)")


if __name__ == "__main__":
    main()
