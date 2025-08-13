# A Lightweight Robinhood API Client

This unofficial API client provides a Python interface for interacting with the Robinhood API. The code is simple to use, easy to understand, and easy to modify. With this library, you can view information on stocks, options, and crypto-currencies in real-time, create your own robo-investor or trading algorithm.


# Installing

There is no need to download these files directly. This project is published on PyPi, so it can be installed by typing into terminal (on Mac) or into command prompt (on PC):

```bash
pip install robinhood-client
```

Also be sure that Python 3 is installed. If you need to install python you can download it from [Python.org](https://www.python.org/downloads/). Pip is the package installer for python, and is automatically installed when you install python. To learn more about Pip, you can go to [PyPi.org](https://pypi.org/project/pip/).

If you would like to be able to make changes to the package yourself, clone the repository onto your computer by typing into the terminal or command prompt:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/robinhood-client.git
cd robinhood-client
```

Now that you have cd into the repository you can type:

```bash
pip install .
```

and this will install whatever you changed in the local files. This will allow you to make changes and experiment with your own code.

## Basic Usage

```python
import robinhood-client as rh

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

See the `examples/logging_example.py` file for a complete example of custom logging configuration.

## More Examples

If you would like to see some example code and instructions on how to set up two-factor authorization, go to the [Documentation](Robinhood.rst).

---

## Contributing

See the [Contributing](/contributing.md) page for info about contributing to this project.

### Build and Install a Wheel

**Build**
```bash
python -m pip install build
python -m build
```

**Install**
```bash
python -m pip install /path/to/robinhood-client/dist/robinhood-client-*.whl
```

### Automatic Testing

If you are contributing to this project and would like to use automatic testing for your changes, you will need to install pytest and pytest-dotenv. To do this, type into terminal or command prompt:

```bash
pip install pytest
pip install pytest-dotenv
```

You will also need to fill out all the fields in `.test.env`. It is recommended to rename the file as `.env` once you are done adding in all your personal information. After that, you can simply run:

```bash
pytest
```

to run all the tests. If you would like to run specific tests or run all the tests in a specific class then type:

```bash
pytest tests/test_robinhood.py -k test_name_apple # runs only the 1 test
```

Finally, if you would like the API calls to print out to terminal, then add the `-s` flag to any of the above pytest calls.

### Updating Documentation

Docs are powered by [Sphinx](https://www.sphinx-doc.org/en/master/tutorial/getting-started.html).

**Build Docs**

```bash
sphinx-build -M html docs/source/ docs/build/
```

---

**Attribution:** This project is a fork of [robin_stocks](https://github.com/jmfernandes/robin_stocks) by Joseph Fernandes. **Robinhood Client** is a slimmed down version that supports only Robinhood and additional enhancements for cloud support, security, and other changes.
