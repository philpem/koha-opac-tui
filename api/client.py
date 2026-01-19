"""
Koha API client for interacting with the Koha ILS REST API.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode, quote
import json
import logging

import httpx

from utils.config import KohaConfig


logger = logging.getLogger(__name__)


@dataclass
class BiblioRecord:
    """Represents a bibliographic record."""
    biblio_id: int
    title: str = ""
    author: str = ""
    publication_year: Optional[str] = None
    publisher: str = ""
    isbn: str = ""
    item_type: str = ""
    call_number: str = ""
    subjects: List[str] = field(default_factory=list)
    notes: str = ""
    edition: str = ""
    physical_description: str = ""
    series: str = ""
    summary: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HoldingItem:
    """Represents an item holding."""
    item_id: int
    barcode: str = ""
    library_id: str = ""
    library_name: str = ""
    location: str = ""
    call_number: str = ""
    copy_number: Optional[int] = None
    status: str = ""
    is_available: bool = True
    due_date: Optional[str] = None
    item_type: str = ""
    notes: str = ""


@dataclass
class SearchResult:
    """Container for search results."""
    records: List[BiblioRecord]
    total_count: int
    page: int
    per_page: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages."""
        if self.per_page <= 0:
            return 1
        return (self.total_count + self.per_page - 1) // self.per_page
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages
    
    @property
    def has_prev(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


class KohaAPIClient:
    """Client for interacting with the Koha REST API."""
    
    def __init__(self, config: KohaConfig):
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None
        self._libraries: Dict[str, str] = {}  # Cache for library names
    
    async def __aenter__(self) -> "KohaAPIClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=self.config.request_timeout,
            follow_redirects=True,
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_public: bool = True,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Make a GET request to the API."""
        if not self._client:
            return None, "Client not initialized"
        
        base_url = self.config.public_api_url if use_public else self.config.staff_api_url
        url = f"{base_url}/{endpoint.lstrip('/')}"
        
        default_headers = {
            "Accept": "application/json",
        }
        if headers:
            default_headers.update(headers)
        
        try:
            response = await self._client.get(url, params=params, headers=default_headers)
            
            if response.status_code == 200:
                # Try to get total count from headers
                total = response.headers.get("X-Total-Count", "0")
                data = response.json()
                if isinstance(data, list):
                    return {"items": data, "total": int(total)}, None
                return data, None
            elif response.status_code == 404:
                return None, "Not found"
            else:
                error_msg = f"API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except:
                    pass
                return None, error_msg
                
        except httpx.TimeoutException:
            return None, "Request timed out"
        except httpx.ConnectError:
            return None, "Could not connect to server"
        except Exception as e:
            logger.exception("API request failed")
            return None, str(e)
    
    async def search_biblios(
        self,
        query: str,
        search_type: str = "title",
        page: int = 1,
        per_page: int = 10,
    ) -> Tuple[Optional[SearchResult], Optional[str]]:
        """
        Search for bibliographic records.
        
        Note: The Koha public API doesn't have a direct search endpoint,
        so we use a title/author filter with -like operator.
        """
        # Build the query filter
        if search_type == "title":
            q_filter = {"title": {"-like": f"%{query}%"}}
        elif search_type == "author":
            q_filter = {"author": {"-like": f"%{query}%"}}
        elif search_type == "isbn":
            q_filter = {"isbn": {"-like": f"%{query}%"}}
        elif search_type == "subject":
            # Subject search is more complex, we'll try title for now
            q_filter = {"title": {"-like": f"%{query}%"}}
        else:
            # Keyword search - search multiple fields
            q_filter = [
                {"title": {"-like": f"%{query}%"}},
                {"author": {"-like": f"%{query}%"}},
            ]
        
        params = {
            "q": json.dumps(q_filter),
            "_page": page,
            "_per_page": per_page,
        }
        
        data, error = await self._get("biblios", params=params)
        
        if error:
            return None, error
        
        if not data:
            return SearchResult([], 0, page, per_page), None
        
        items = data.get("items", [])
        total = data.get("total", len(items))
        
        records = []
        for item in items:
            record = self._parse_biblio_json(item)
            records.append(record)
        
        return SearchResult(records, total, page, per_page), None
    
    async def get_biblio(self, biblio_id: int) -> Tuple[Optional[BiblioRecord], Optional[str]]:
        """Get a single bibliographic record by ID."""
        data, error = await self._get(f"biblios/{biblio_id}")
        
        if error:
            return None, error
        
        if not data:
            return None, "Record not found"
        
        return self._parse_biblio_json(data), None
    
    async def get_biblio_items(self, biblio_id: int) -> Tuple[List[HoldingItem], Optional[str]]:
        """Get items (holdings) for a bibliographic record."""
        data, error = await self._get(f"biblios/{biblio_id}/items")
        
        if error:
            return [], error
        
        if not data:
            return [], None
        
        items_data = data.get("items", []) if isinstance(data, dict) else data
        
        holdings = []
        for item in items_data:
            holding = self._parse_item_json(item)
            holdings.append(holding)
        
        return holdings, None
    
    async def get_libraries(self) -> Tuple[Dict[str, str], Optional[str]]:
        """Get list of libraries."""
        if self._libraries:
            return self._libraries, None
        
        data, error = await self._get("libraries")
        
        if error:
            return {}, error
        
        if not data:
            return {}, None
        
        items = data.get("items", []) if isinstance(data, dict) else data
        
        for lib in items:
            lib_id = lib.get("library_id", "")
            lib_name = lib.get("name", lib_id)
            self._libraries[lib_id] = lib_name
        
        return self._libraries, None
    
    def _parse_biblio_json(self, data: Dict[str, Any]) -> BiblioRecord:
        """Parse a biblio JSON response into a BiblioRecord."""
        return BiblioRecord(
            biblio_id=data.get("biblio_id", 0),
            title=data.get("title", "Unknown Title"),
            author=data.get("author", ""),
            publication_year=data.get("copyright_date") or data.get("publication_year"),
            publisher=data.get("publisher", ""),
            isbn=data.get("isbn", ""),
            item_type=data.get("item_type", ""),
            call_number=data.get("cn_sort", "") or data.get("callnumber", ""),
            subjects=[],  # Would need MARC parsing
            notes=data.get("notes", ""),
            edition=data.get("edition", ""),
            physical_description=data.get("pages", ""),
            series=data.get("serial", ""),
            summary=data.get("abstract", ""),
            raw_data=data,
        )
    
    def _parse_item_json(self, data: Dict[str, Any]) -> HoldingItem:
        """Parse an item JSON response into a HoldingItem."""
        # Determine availability
        not_for_loan = data.get("not_for_loan_status", 0)
        lost_status = data.get("lost_status", 0)
        damaged_status = data.get("damaged_status", 0)
        withdrawn = data.get("withdrawn", 0)
        checked_out = data.get("checked_out_date") is not None
        
        is_available = (
            not_for_loan == 0 and
            lost_status == 0 and
            damaged_status == 0 and
            withdrawn == 0 and
            not checked_out
        )
        
        # Determine status text
        if checked_out:
            status = "On Loan"
        elif lost_status:
            status = "Lost"
        elif damaged_status:
            status = "Damaged"
        elif withdrawn:
            status = "Withdrawn"
        elif not_for_loan:
            status = "Reference Only"
        else:
            status = "Available"
        
        library_id = data.get("holding_library_id", "") or data.get("home_library_id", "")
        
        return HoldingItem(
            item_id=data.get("item_id", 0),
            barcode=data.get("barcode", ""),
            library_id=library_id,
            library_name=self._libraries.get(library_id, library_id),
            location=data.get("location", ""),
            call_number=data.get("callnumber", ""),
            copy_number=data.get("copy_number"),
            status=status,
            is_available=is_available,
            due_date=data.get("due_date"),
            item_type=data.get("item_type_id", ""),
            notes=data.get("public_note", ""),
        )


# Singleton-ish access for the API client
_api_client: Optional[KohaAPIClient] = None


async def get_api_client(config: KohaConfig) -> KohaAPIClient:
    """Get or create the API client."""
    global _api_client
    if _api_client is None:
        _api_client = KohaAPIClient(config)
    return _api_client
