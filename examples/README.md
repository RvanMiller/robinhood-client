# Examples

This directory contains example scripts demonstrating how to use the Robinhood Client library.

## Available Examples

### `cursor_example.py`
Demonstrates the cursor pattern for paginated data retrieval.

### `options_example.py`
Shows how to retrieve options order data using the OptionsDataClient:
- Get recent options orders with filtering
- Retrieve specific orders by ID
- Use cursor pagination to iterate through all orders
- Manual cursor navigation

## Running Examples

Before running any examples, ensure you have set the required environment variables:

```bash
export RH_USERNAME="your_username"
export RH_PASSWORD="your_password"
export RH_MFA_CODE="your_mfa_secret"
export RH_ACCOUNT_NUMBER="your_account_number"
```

Then run an example:

```bash
python examples/options_example.py
```

**Note**: Examples that interact with the API require valid Robinhood credentials and will make real API calls.