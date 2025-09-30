"""Default logging configuration for Robinhood Client."""

import logging
import sys
import os


# Track configuration state to ensure idempotent behavior
_logging_configured = False


def configure_logging(level=None, log_file=None):
    """Configure logging for the robinhood_client package.

    This function sets up logging handlers and formatters for the package,
    allowing logs to be displayed in the console and optionally written to a file.

    Args:
        level (int, optional): The logging level to use. Defaults to INFO or value from
                               ROBINHOOD_LOG_LEVEL environment variable if set.
        log_file (str, optional): Path to a log file. If provided, logs will be written to this file.
                                 Defaults to None or value from ROBINHOOD_LOG_FILE env variable if set.

    Returns:
        logging.Logger: The configured logger object
    """
    global _logging_configured
    
    # Get root logger for the package
    logger = logging.getLogger("robinhood_client")

    # Clear any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Reset configuration state when explicitly called
    _logging_configured = False

    # Determine log level - environment variable takes precedence
    if level is None:
        env_level = os.environ.get("ROBINHOOD_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    logger.setLevel(level)

    # Create console handler for terminal output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter and add it to the handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified or in environment variable
    log_file = log_file or os.environ.get("ROBINHOOD_LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Mark as configured
    _logging_configured = True

    return logger
