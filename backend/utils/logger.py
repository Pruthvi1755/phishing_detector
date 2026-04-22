"""
Centralised logging configuration for PhishGuard backend.
All modules import get_logger() from here to ensure consistent formatting.
"""

import logging
import sys
import os

_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=_LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        logging.Logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Server started")
    """
    return logging.getLogger(name)
