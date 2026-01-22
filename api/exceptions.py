"""
Custom exception hierarchy for Koha API client.

Using typed exceptions instead of string error messages provides:
- Better error handling with specific exception types
- More informative error messages with context
- Easier debugging and logging
- Type-safe error handling
"""


class KohaAPIError(Exception):
    """
    Base exception for all Koha API errors.

    All custom exceptions inherit from this base class, allowing
    callers to catch all Koha-related errors with a single except clause.
    """
    pass


class KohaConnectionError(KohaAPIError):
    """
    Raised when unable to connect to the Koha server.

    This includes network errors, DNS failures, and connection timeouts.
    """

    def __init__(self, message: str = "Cannot connect to Koha server", url: str = None):
        self.url = url
        if url:
            message = f"{message}: {url}"
        super().__init__(message)


class KohaAuthenticationError(KohaAPIError):
    """
    Raised when authentication fails (invalid credentials).

    This indicates the provided username/password or API key is invalid.
    """

    def __init__(self, message: str = "Invalid credentials or authentication failed"):
        super().__init__(message)


class KohaAuthorizationError(KohaAPIError):
    """
    Raised when the authenticated user lacks permission for the requested operation.

    This indicates valid credentials but insufficient permissions (403 Forbidden).
    """

    def __init__(self, message: str = "Insufficient permissions for this operation"):
        super().__init__(message)


class KohaBiblioNotFoundError(KohaAPIError):
    """
    Raised when a requested bibliographic record is not found.

    This indicates the biblio_id doesn't exist in the catalog.
    """

    def __init__(self, biblio_id: int, message: str = None):
        self.biblio_id = biblio_id
        if message is None:
            message = f"Bibliographic record {biblio_id} not found"
        super().__init__(message)


class KohaItemNotFoundError(KohaAPIError):
    """
    Raised when a requested item/holding is not found.

    This indicates the item_id doesn't exist in the catalog.
    """

    def __init__(self, item_id: int, message: str = None):
        self.item_id = item_id
        if message is None:
            message = f"Item {item_id} not found"
        super().__init__(message)


class KohaBadRequestError(KohaAPIError):
    """
    Raised when the API request is malformed or invalid.

    This indicates incorrect parameters, invalid query syntax, or
    other client-side request errors (400 Bad Request).
    """

    def __init__(self, message: str = "Invalid request parameters", details: str = None):
        self.details = details
        if details:
            message = f"{message}: {details}"
        super().__init__(message)


class KohaServerError(KohaAPIError):
    """
    Raised when the Koha server encounters an internal error.

    This indicates a server-side error (500 Internal Server Error).
    """

    def __init__(self, message: str = "Koha server error", status_code: int = None):
        self.status_code = status_code
        if status_code:
            message = f"{message} (HTTP {status_code})"
        super().__init__(message)


class KohaTimeoutError(KohaAPIError):
    """
    Raised when a request to the Koha server times out.

    This indicates the server took too long to respond.
    """

    def __init__(self, message: str = "Request timed out", timeout: int = None):
        self.timeout = timeout
        if timeout:
            message = f"{message} after {timeout}s"
        super().__init__(message)


class KohaParseError(KohaAPIError):
    """
    Raised when unable to parse the response from Koha.

    This indicates unexpected response format, invalid JSON/HTML, or
    MARC parsing errors.
    """

    def __init__(self, message: str = "Failed to parse response", details: str = None):
        self.details = details
        if details:
            message = f"{message}: {details}"
        super().__init__(message)
