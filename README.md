![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/RvanMiller/robinhood-client/ci-publish.yml?label=tests)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/robinhood-client)
![GitHub License](https://img.shields.io/github/license/RvanMiller/robinhood-client)


# A Lightweight Robinhood API Client

🚧 Under Construction 🚧

This unofficial API client provides a Python interface for interacting with the Robinhood API. The code is simple to use, easy to understand, and easy to modify. With this library, you can retrieve information on stocks and options orders, manage authentication with session persistence, and work with paginated data using an intuitive cursor pattern.

## Current Features

- **Stock Orders**: Retrieve and paginate through stock order history
- **Options Orders**: Access options trading data with detailed leg information
- **Session Management**: Persistent authentication with filesystem or AWS S3 storage
- **Cursor Pagination**: Efficient handling of large datasets
- **MFA Support**: Time-based one-time password (TOTP) authentication
- **Cloud Ready**: Designed for both local development and cloud deployments

## Roadmap

This is a focused rewrite that currently supports data retrieval. Trading functionality is planned for future releases. See [roadmap.md](roadmap.md) for details.

## Versioning

This project follows [Semantic Versioning 2.0](https://semver.org). Currently in major version 0.x for initial development, which means the API and features are unstable and may change. For stable usage, please check back when version 1.x is released.

# Installing

This project is published on PyPi, so it can be installed by typing into terminal (on Mac) or into command prompt (on PC):

```bash
# Using pip
pip install robinhood-client

# Using Poetry
poetry add robinhood-client
```

Also be sure that Python 3.10 or higher is installed. If you need to install python you can download it from [Python.org](https://www.python.org/downloads/).

## Basic Usage

```python
from robinhood_client.common.session import FileSystemSessionStorage
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.data.options import OptionsDataClient
from robinhood_client.data.requests import StockOrdersRequest, OptionsOrdersRequest
import pyotp

# Set up session storage
session_storage = FileSystemSessionStorage()

# Create and authenticate a client
orders_client = OrdersDataClient(session_storage=session_storage)

# Login with MFA support
totp = pyotp.TOTP("your_mfa_secret").now()
orders_client.login(
    username="your_username", 
    password="your_password", 
    mfa_code=totp
)

# Get stock orders with pagination support
request = StockOrdersRequest(account_number="your_account_number", page_size=10)
stock_orders = orders_client.get_stock_orders(request)

# Access current page results
for order in stock_orders.results:
    print(f"Order {order.id}: {order.state} - {order.side} {order.quantity}")

# Iterate through all pages automatically
for order in stock_orders:
    print(f"Order {order.id}: {order.state}")

# Options client usage
options_client = OptionsDataClient(session_storage=session_storage)
options_client.login(username="your_username", password="your_password", mfa_code=totp)

options_request = OptionsOrdersRequest(account_number="your_account_number")
options_orders = options_client.get_options_orders(options_request)

for order in options_orders.results:
    print(f"Options order: {order.chain_symbol} - ${order.premium}")
```

## Examples

The `examples/` directory contains working examples that demonstrate key features:

- **`cursor_example.py`**: Demonstrates cursor-based pagination for retrieving large datasets
- **`options_example.py`**: Shows options order retrieval, filtering, and data processing

To run the examples, set the required environment variables:

```bash
export RH_USERNAME="your_username"
export RH_PASSWORD="your_password"
export RH_MFA_CODE="your_mfa_secret"
export RH_ACCOUNT_NUMBER="your_account_number"
```

Then run:

```bash
python examples/options_example.py
```

**Note**: Examples make real API calls and require valid Robinhood credentials.

## Development Tools

### Bruno API Collection

The `tools/Bruno/` directory contains a [Bruno](https://www.usebruno.com/) API collection for testing and exploring Robinhood endpoints. The collection includes pre-configured requests organized by service (Account, Auth, Options, etc.) and mirrors the endpoints used in this Python library. See the [Bruno README](tools/Bruno/README.md) for setup instructions.

## Logging

The library includes a configurable logging system that works both when used as a library and when run as a script.

### Default Behavior

By default, logs are configured at the INFO level and output to the console. This happens automatically when you import the package:

```python
import robinhood_client
from robinhood_client.data.orders import OrdersDataClient
from robinhood_client.common.session import FileSystemSessionStorage

# Logs will appear in the console at INFO level
session_storage = FileSystemSessionStorage()
client = OrdersDataClient(session_storage=session_storage)
client.login(username="your_username", password="your_password")
```

### Customizing Logging

You can customize the logging behavior using the `configure_logging` function:

```python
from robinhood_client.common.logging import configure_logging
import logging

# Set custom log level and optionally log to a file
configure_logging(
    level=logging.DEBUG,  # More detailed logs
    log_file="robinhood.log"  # Also write logs to this file
)
```

### Environment Variables

You can also configure logging using environment variables:

- `ROBINHOOD_LOG_LEVEL`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `ROBINHOOD_LOG_FILE`: Path to a log file where logs will be written

Example:
```bash
# On Linux/Mac
export ROBINHOOD_LOG_LEVEL=DEBUG
export ROBINHOOD_LOG_FILE=~/robinhood.log

# On Windows
set ROBINHOOD_LOG_LEVEL=DEBUG
set ROBINHOOD_LOG_FILE=C:\logs\robinhood.log
```

### Using in Cloud Environments

When deploying to cloud environments, the logging system will respect the configured log levels and can write to a file or stdout as needed, making it suitable for containerized environments and cloud logging systems.

---

## Contributing

See the [Contributing](/contributing.md) page for info about contributing to this project.

### Dependency Management with Poetry

This project uses Poetry for dependency management. Here are some common commands:

#### Installing Dependencies

```bash
# Install all dependencies (including development dependencies)
poetry install
```

#### Managing Dependencies

```bash
# Add a new dependency
poetry add package-name

# Add a development dependency
poetry add --group dev package-name

# Remove a dependency
poetry remove package-name
```

#### Updating Dependencies

```bash
# Update all dependencies according to the version constraints in pyproject.toml
poetry update

# Update a specific package
poetry update package-name

# Show outdated dependencies that can be updated
poetry show --outdated
```


### Install Dev Dependencies

```bash
# Using pip
pip install -e .[dev]

# Using Poetry
poetry install
```


### Automatic Testing

If you are contributing to this project and would like to use automatic testing for your changes, you will need to install pytest and pytest-dotenv.

```bash
# Using pip
pip install pytest
pip install pytest-dotenv

# Using Poetry (dev dependencies are automatically installed)
poetry install
```

You will also need to fill out all the fields in `.test.env`. It is recommended to rename the file as `.env` once you are done adding in all your personal information. Set the following environment variables:

- `RH_USERNAME`: Your Robinhood username
- `RH_PASSWORD`: Your Robinhood password  
- `RH_MFA_CODE`: Your MFA secret (for TOTP generation)
- `RH_ACCOUNT_NUMBER`: Your Robinhood account number

After that, you can run the tests:

```bash
# Using pip
pytest tests/unit/  # Run unit tests only

# Using Poetry
poetry run pytest tests/unit/
```

To run integration tests (requires valid credentials):

```bash
# Using pip
pytest tests/integration/

# Using Poetry
poetry run pytest tests/integration/
```

To run specific tests or run all the tests in a specific class:

```bash
# Using pip
pytest tests/unit/data/orders_tests.py -k test_specific_function

# Using Poetry
poetry run pytest tests/unit/data/orders_tests.py -k test_specific_function
```

Finally, if you would like the API calls to print out to terminal, then add the `-s` flag to any of the above pytest calls.

### Linting

The project uses `ruff` for linting.

```bash
# Using Poetry with ruff
poetry run ruff check .
```

### Updating Documentation

Docs are powered by [Sphinx](https://www.sphinx-doc.org/en/master/tutorial/getting-started.html).

```bash
# Using pip
cd docs
make html

# Using Poetry
cd docs
poetry run make html
```

**Build Docs**

```bash
sphinx-build -M html docs/source/ docs/build/
```

---

**Attribution:** This project is a fork of [robin_stocks](https://github.com/jmfernandes/robin_stocks) by Joseph Fernandes. **Robinhood Client** is a rewritten version that is OOP-based, has efficiency upgrades, cloud support, a modern CI/CD development workflow, and more.

## Legal Disclaimers

**⚠️ Independent Project:** This project is not affiliated with, endorsed, or sponsored by Robinhood Markets, Inc. This is an independent open-source project developed by the community.

**⚠️ Investment Risk:** Trading stocks and options involves significant financial risk and may result in substantial losses. Past performance does not guarantee future results. Please consult with a qualified financial advisor before making investment decisions. Use this software at your own risk.
