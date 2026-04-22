"""
URL Validator
Lightweight structural validation before feature extraction.
"""

import re
from urllib.parse import urlparse
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Regex for a reasonable URL (allows http/https/ftp)
_URL_PATTERN = re.compile(
    r"^(https?|ftp)://"          # scheme
    r"[^\s/$.?#].[^\s]*$",       # non-whitespace body
    re.IGNORECASE,
)

MAX_URL_LENGTH = 2048


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate that a string is a structurally sound URL.

    Args:
        url: The raw URL string to check.

    Returns:
        (True, "") if valid, or (False, "<reason>") if invalid.

    Example:
        >>> validate_url("https://example.com")
        (True, '')
        >>> validate_url("not-a-url")
        (False, 'URL must start with http:// or https://')
    """
    if not url or not url.strip():
        return False, "URL must not be empty."

    url = url.strip()

    if len(url) > MAX_URL_LENGTH:
        return False, f"URL exceeds maximum length of {MAX_URL_LENGTH} characters."

    if " " in url:
        return False, "URL must not contain spaces."

    if not _URL_PATTERN.match(url):
        if not url.startswith(("http://", "https://", "ftp://")):
            return False, "URL must start with http:// or https://"
        return False, "URL format is invalid."

    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "URL is missing a domain/host."
    except Exception as exc:
        logger.warning("URL parse error for '%s': %s", url, exc)
        return False, f"Could not parse URL: {exc}"

    return True, ""
