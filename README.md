![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/RvanMiller/robinhood-client/ci-publish.yml?label=tests)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/robinhood-client)
![GitHub License](https://img.shields.io/github/license/RvanMiller/robinhood-client)


# A Lightweight Robinhood API Client

🚧 Under Construction 🚧

This unofficial API client provides a Python interface for interacting with the Robinhood API. The code is simple to use, easy to understand, and easy to modify. With this library, you can view information on stocks, options, and crypto-currencies in real-time, create your own robo-investor or trading algorithm.

# Installing

There is no need to download these files directly. This project is published on PyPi, so it can be installed by typing into terminal (on Mac) or into command prompt (on PC):

```bash
# Using pip
pip install robinhood-client

# Using Poetry
poetry add robinhood-client
```

Also be sure that Python 3.10 or higher is installed. If you need to install python you can download it from [Python.org](https://www.python.org/downloads/).

## Basic Usage

```python
import robinhood_client as rh

# Gets all crypto orders from Robinhood that are opened
rh.get_all_open_crypto_orders() 
```

## Logging

The library includes a configurable logging system that works both when used as a library and when run as a script.

### Default Behavior

By default, logs are configured at the INFO level and output to the console. This happens automatically when you import the package:

```python
import robinhood_client

# Logs will appear in the console at INFO level
robinhood_client.login(username="your_username", password="your_password")
```

### Customizing Logging

You can customize the logging behavior using the `configure_logging` function:

```python
from robinhood_client.logging import configure_logging
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

#### Building and Publishing

```bash
# Build the package
poetry build

# Publish to PyPI
poetry publish
```

### Install Dev Dependencies

```bash
# Using pip
pip install -e .[dev]

# Using Poetry
poetry install
```

### Build and Install a Wheel

**Build**
```bash
# Using pip
python -m pip install build
python -m build

# Using Poetry
poetry build
```

**Install Wheel**
```bash
# Using pip
python -m pip install /path/to/robinhood-client/dist/robinhood-client-*.whl

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

You will also need to fill out all the fields in `.test.env`. It is recommended to rename the file as `.env` once you are done adding in all your personal information. After that, you can run the tests:

```bash
# Using pip
pytest

# Using Poetry
poetry run pytest
```

To run specific tests or run all the tests in a specific class:

```bash
# Using pip
pytest tests/test_robinhood.py -k test_name_apple # runs only the 1 test

# Using Poetry
poetry run pytest tests/test_robinhood.py -k test_name_apple
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

**Attribution:** This project is a fork of [robin_stocks](https://github.com/jmfernandes/robin_stocks) by Joseph Fernandes. **Robinhood Client** is a slimmed down version that supports only Robinhood and additional enhancements for cloud support, security, and other changes.
