# log_manager.py
import logging
import logging.config
from .log_config import LOGGING
from .issue_tracking import IssueTrackingHandler

# Apply the logging config once
logging.config.dictConfig(LOGGING)

# Set up issue tracker handler (shared across all modules)
issue_tracker = IssueTrackingHandler()
logging.getLogger().addHandler(issue_tracker)


def get_logger(name: str) -> logging.Logger:
    """Retrieves a logger instance by name.

    This function simplifies getting a logger and ensures consistent setup
    with the project's logging configuration.

    Args:
        name: The name of the logger to retrieve.

    Returns:
        A logger instance with the specified name.
    """
    return logging.getLogger(name)
