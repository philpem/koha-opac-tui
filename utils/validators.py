"""
Input validation functions for the Koha OPAC TUI.

Provides validation for user inputs, configuration values, and API parameters
to ensure data integrity and provide helpful error messages.
"""

from typing import Tuple, Optional
from urllib.parse import urlparse


# Validation constants
MIN_SEARCH_QUERY_LENGTH = 2
MAX_SEARCH_QUERY_LENGTH = 500
MIN_TIMEOUT = 1
MAX_TIMEOUT = 300  # 5 minutes
MIN_ITEMS_PER_PAGE = 1
MAX_ITEMS_PER_PAGE = 100


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a search query string.

    Args:
        query: The search query to validate

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    if not query:
        return False, "Search query cannot be empty"

    query = query.strip()

    if len(query) < MIN_SEARCH_QUERY_LENGTH:
        return False, f"Search query must be at least {MIN_SEARCH_QUERY_LENGTH} characters"

    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        return False, f"Search query too long (max {MAX_SEARCH_QUERY_LENGTH} characters)"

    return True, None


def validate_url(url: str, require_https: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate a URL string.

    Args:
        url: The URL to validate
        require_https: If True, only allow HTTPS URLs

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    if not url:
        return False, "URL cannot be empty"

    url = url.strip()

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Invalid URL format"

    if not parsed.scheme:
        return False, "URL must include a scheme (http:// or https://)"

    if parsed.scheme not in ('http', 'https'):
        return False, f"URL scheme must be http or https, got: {parsed.scheme}"

    if require_https and parsed.scheme != 'https':
        return False, "URL must use HTTPS for security"

    if not parsed.netloc:
        return False, "URL must include a hostname"

    return True, None


def validate_timeout(timeout: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a timeout value in seconds.

    Args:
        timeout: Timeout value in seconds

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(timeout, int):
        return False, "Timeout must be an integer"

    if timeout < MIN_TIMEOUT:
        return False, f"Timeout must be at least {MIN_TIMEOUT} second(s)"

    if timeout > MAX_TIMEOUT:
        return False, f"Timeout too large (max {MAX_TIMEOUT} seconds / {MAX_TIMEOUT // 60} minutes)"

    return True, None


def validate_items_per_page(items_per_page: int) -> Tuple[bool, Optional[str]]:
    """
    Validate items per page setting.

    Args:
        items_per_page: Number of items to display per page

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(items_per_page, int):
        return False, "Items per page must be an integer"

    if items_per_page < MIN_ITEMS_PER_PAGE:
        return False, f"Items per page must be at least {MIN_ITEMS_PER_PAGE}"

    if items_per_page > MAX_ITEMS_PER_PAGE:
        return False, f"Items per page too large (max {MAX_ITEMS_PER_PAGE})"

    return True, None


def validate_biblio_id(biblio_id: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a bibliographic record ID.

    Args:
        biblio_id: The bibliographic record ID

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(biblio_id, int):
        return False, "Biblio ID must be an integer"

    if biblio_id <= 0:
        return False, "Biblio ID must be positive"

    return True, None


def validate_page_number(page: int) -> Tuple[bool, Optional[str]]:
    """
    Validate a pagination page number.

    Args:
        page: The page number

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(page, int):
        return False, "Page number must be an integer"

    if page < 1:
        return False, "Page number must be at least 1"

    return True, None
