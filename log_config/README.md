# logtools

**Centralized logging setup and issue tracking for Python applications**

This package provides a reusable and extensible logging setup, including:

- Centralized logging configuration (JSON formatted output)
- Logging to both stdout and a rotating file
- A custom logging handler that tracks warnings and errors
- A simple interface to get a logger and check for parsing issues across modules

## 📦 Installation

If this is part of your application’s source:

```bash
pip install -e .
```

Or simply ensure the `logtools/` directory is in your Python path.

## 🚀 Quickstart

### 1. Import the logger and issue tracker

In any module where you want to log:

```python
from logtools import get_logger, issue_tracker

logger = get_logger(__name__)
logger.info("This is a log message.")
logger.warning("This warning will be tracked.")

if issue_tracker.has_issues():
    print("Issues found:", issue_tracker.get_issues())
else:
    print("All clear.")
```

### 2. What gets logged

The logging output is JSON-formatted and includes timestamps, level, message, module, function name, and process ID. By default:

- Logs are printed to **stdout**
- Logs are written to a rotating file named `log.json`

### 3. What gets tracked

Only logs at level `WARNING` or higher are tracked in memory by the custom `IssueTrackingHandler`. This allows you to:

- Log issues as you go
- Check at the end whether any issues occurred during execution

## 🧱 Package Structure

```
logtools/
├── __init__.py            # Public API: get_logger, issue_tracker
├── logging_config.py      # Dict-based logging setup
├── log_manager.py         # Applies config and exposes logger + tracker
└── issue_tracking.py      # Custom handler that tracks issues
```

## 🔍 Customization

- You can modify `logging_config.py` to use a different formatter or log to additional destinations (e.g., syslog, external services).
- The `IssueTrackingHandler` can be extended to collect additional context like timestamps or thread info.

## ✅ License

This package is internal to your application and unlicensed unless explicitly stated.
