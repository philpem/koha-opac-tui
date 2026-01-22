"""API client modules for the Koha OPAC TUI."""

from .client import (
    KohaAPIClient,
    BiblioRecord,
    HoldingItem,
    SearchResult,
    get_api_client,
)
from .mock_client import MockKohaAPIClient
from .exceptions import (
    KohaAPIError,
    KohaConnectionError,
    KohaAuthenticationError,
    KohaAuthorizationError,
    KohaBiblioNotFoundError,
    KohaItemNotFoundError,
    KohaBadRequestError,
    KohaServerError,
    KohaTimeoutError,
    KohaParseError,
)

__all__ = [
    "KohaAPIClient",
    "MockKohaAPIClient",
    "BiblioRecord",
    "HoldingItem",
    "SearchResult",
    "get_api_client",
    # Exceptions
    "KohaAPIError",
    "KohaConnectionError",
    "KohaAuthenticationError",
    "KohaAuthorizationError",
    "KohaBiblioNotFoundError",
    "KohaItemNotFoundError",
    "KohaBadRequestError",
    "KohaServerError",
    "KohaTimeoutError",
    "KohaParseError",
]
