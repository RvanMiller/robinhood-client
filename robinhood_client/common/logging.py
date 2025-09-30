"""Default logging configuration for Robinhood Client."""

import logging
import sys
import os


# Track configuration state to ensure idempotent behavior
_logging_configured = False
_current_level = None
_current_log_file = None


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
    global _logging_configured, _current_level, _current_log_file

    # Get root logger for the package
    logger = logging.getLogger("robinhood_client")

    # Determine log level - environment variable takes precedence
    if level is None:
        env_level = os.environ.get("ROBINHOOD_LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    # Get log file setting
    log_file = log_file or os.environ.get("ROBINHOOD_LOG_FILE")

    # If already configured with same settings, return early to prevent reconfiguration
    if (
        _logging_configured
        and _current_level == level
        and _current_log_file == log_file
    ):
        return logger

    # Clear any existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

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

    # Add file handler if log_file is specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Mark as configured and store current settings
    _logging_configured = True
    _current_level = level
    _current_log_file = log_file

    return logger
