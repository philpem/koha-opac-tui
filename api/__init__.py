"""API client modules for the Koha OPAC TUI."""

from .client import (
    KohaAPIClient,
    BiblioRecord,
    HoldingItem,
    SearchResult,
)
from .mock_client import MockKohaAPIClient

__all__ = [
    "KohaAPIClient",
    "MockKohaAPIClient",
    "BiblioRecord",
    "HoldingItem",
    "SearchResult",
]
