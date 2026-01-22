"""
Centralized logging configuration for the Koha OPAC TUI.

This module provides a single point of configuration for logging to avoid
duplicate log handlers and inconsistent formatting across modules.
"""

import logging
from pathlib import Path


# Default log file location
DEFAULT_LOG_FILE = '/tmp/koha_tui_debug.log'


def setup_logger(name: str, log_file: str = DEFAULT_LOG_FILE) -> logging.Logger:
    """
    Get or create a logger with consistent configuration.

    Args:
        name: The logger name (typically __name__ from the calling module)
        log_file: Path to the log file (default: /tmp/koha_tui_debug.log)

    Returns:
        Configured logger instance

    Note:
        This function is idempotent - calling it multiple times with the same
        name will return the same logger without adding duplicate handlers.
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured (prevents duplicate handlers)
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger
