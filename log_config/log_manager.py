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


def get_logger(name: str):
    return logging.getLogger(name)
