"""
Configuration file for pytest.
This file contains hooks and fixtures that customize the behavior of pytest for this project.
"""
import pytest
from robinhood_client.common.logging import configure_logging


@pytest.fixture(autouse=True)
def setup_logging():
    """
    Configure logging for tests using the project's built-in logging configuration.
    
    This fixture is automatically used in all tests and ensures that
    logging is properly configured to capture DEBUG level logs.
    """
    # Configure the robinhood_client logger to DEBUG level for tests
    logger = configure_logging(level='DEBUG')
    return logger
