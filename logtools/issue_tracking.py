import logging
import csv


class IssueTrackingHandler(logging.Handler):
    """A logging handler that stores log records as issues.

    This handler captures log records with severity level WARNING or higher
    and stores them as dictionaries in an internal list. It provides methods
    to check for the presence of issues, retrieve the list of issues, and
    export the issues to a CSV file.
    """

    def __init__(self):
        super().__init__()
        self.issues = []

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record.

        Args:
            record: The log record to emit.
        """
        if record.levelno >= logging.WARNING:
            self.issues.append(
                {
                    "severity": record.levelname,
                    "message": record.getMessage(),
                    "module": record.module,
                    "line": record.lineno,
                    "func": record.funcName,
                }
            )

    def has_issues(self) -> bool:
        """Check if any issues have been logged.

        Returns:
            True if issues exist, False otherwise.
        """
        return bool(self.issues)

    def get_issues(self) -> list:
        """Retrieve the list of logged issues.

        Returns:
            A list of issue dictionaries.
        """
        return self.issues

    def write_csv(self, file_csv: str) -> None:
        """Export the logged issues to a CSV file.

        Args:
            file_csv: The path to the CSV file.
        """
        with open(file_csv, "w", encoding="utf8", newline="") as output_file:
            fc = csv.DictWriter(
                output_file,
                fieldnames=self.issues[0].keys(),
                dialect="excel",
                quoting=csv.QUOTE_STRINGS,
            )
            fc.writeheader()
            fc.writerows(self.issues)
