"""
Centralized logging configuration for the Koha OPAC TUI.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Default log directory follows XDG Base Directory spec
DEFAULT_LOG_DIR = Path.home() / ".local" / "share" / "koha-opac-tui"
DEFAULT_LOG_FILE = "debug.log"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_LOG_BACKUPS = 3

# Track if logging has been configured
_logging_configured = False


def setup_logging(
    level: int = logging.DEBUG,
    log_dir: Path | None = None,
    log_file: str = DEFAULT_LOG_FILE,
    enabled: bool | None = None,
) -> logging.Logger:
    """
    Set up centralized logging for the application.

    Args:
        level: Logging level (default: DEBUG)
        log_dir: Directory for log files (default: ~/.local/share/koha-opac-tui)
        log_file: Name of the log file (default: debug.log)
        enabled: Whether logging is enabled. If None, checks KOHA_DEBUG env var.
                 Set to False to disable file logging entirely.

    Returns:
        The root logger for the application.
    """
    global _logging_configured

    # Determine if logging should be enabled
    if enabled is None:
        enabled = os.environ.get("KOHA_DEBUG", "").lower() in ("1", "true", "yes")

    # Get the root logger for our application
    root_logger = logging.getLogger("koha_opac_tui")

    # Only configure once
    if _logging_configured:
        return root_logger

    if not enabled:
        # Set up a null handler to suppress logging
        root_logger.addHandler(logging.NullHandler())
        root_logger.setLevel(logging.WARNING)
        _logging_configured = True
        return root_logger

    # Use provided or default log directory
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR

    # Ensure log directory exists with appropriate permissions
    log_dir.mkdir(parents=True, exist_ok=True)

    # Set up rotating file handler
    log_path = log_dir / log_file
    handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_SIZE,
        backupCount=MAX_LOG_BACKUPS,
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))

    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    _logging_configured = True
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: The module name (typically __name__)

    Returns:
        A logger instance that is a child of the application root logger.
    """
    # Ensure logging is set up
    if not _logging_configured:
        setup_logging()

    # Create child logger under our root
    if name.startswith("koha_opac_tui."):
        return logging.getLogger(name)
    return logging.getLogger(f"koha_opac_tui.{name}")
