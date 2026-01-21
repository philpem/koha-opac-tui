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


# Set up file-based logging for debugging
logger = logging.getLogger(__name__)
_debug_handler = logging.FileHandler('/tmp/koha_tui_debug.log')
_debug_handler.setLevel(logging.DEBUG)
_debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_debug_handler)
logger.setLevel(logging.DEBUG)


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
    call_number: str = ""  # Kept for backward compatibility
    call_number_lcc: str = ""  # Library of Congress Classification (050)
    call_number_dewey: str = ""  # Dewey Decimal Classification (082)
    subjects: List[str] = field(default_factory=list)
    notes: str = ""
    edition: str = ""
    physical_description: str = ""
    series: str = ""
    summary: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def get_call_number(self, display_mode: str = "both") -> str:
        """Get call number based on display mode setting.
        
        Args:
            display_mode: "lcc" for LOC only, "dewey" for Dewey only, "both" for both
        
        Returns:
            Formatted call number string
        """
        if display_mode == "lcc":
            return self.call_number_lcc or self.call_number or ""
        elif display_mode == "dewey":
            return self.call_number_dewey or self.call_number or ""
        else:  # "both"
            parts = []
            if self.call_number_lcc:
                parts.append(f"LOC: {self.call_number_lcc}")
            if self.call_number_dewey:
                parts.append(f"DDC: {self.call_number_dewey}")
            if parts:
                return " | ".join(parts)
            return self.call_number or ""


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
    public_note: str = ""  # Public note for the item


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
        
        logger.debug(f"GET {url} params={params}")
        
        try:
            response = await self._client.get(url, params=params, headers=default_headers)
            
            logger.debug(f"Response: {response.status_code}")
            
            if response.status_code == 200:
                # Try to get total count from headers
                total = response.headers.get("X-Total-Count", "0")
                data = response.json()
                logger.debug(f"Data type: {type(data)}, total header: {total}")
                if isinstance(data, list):
                    return {"items": data, "total": int(total) if total else len(data)}, None
                return data, None
            elif response.status_code == 404:
                return None, "Not found"
            elif response.status_code == 400:
                # Bad request - likely query format issue
                try:
                    error_data = response.json()
                    logger.debug(f"400 error: {error_data}")
                    if "error" in error_data:
                        return None, f"Bad request: {error_data['error']}"
                    if "errors" in error_data:
                        return None, f"Bad request: {error_data['errors']}"
                except:
                    pass
                return None, "Bad request - query format may not be supported"
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
        
        Uses the OPAC CGI search endpoint which is the most reliable method
        and uses the same search engine as the web OPAC.
        """
        logger.debug(f"search_biblios called with query='{query}', search_type='{search_type}'")
        
        # Use the SVC/CGI search endpoint - most reliable for OPAC-style search
        result, error = await self._search_via_svc(query, search_type, page, per_page)
        logger.debug(f"_search_via_svc returned: records={len(result.records) if result else 0}, error={error}")
        
        if result and result.records:
            return result, None
        
        # If we got here with an error, return it
        if error:
            return None, error
            
        return SearchResult([], 0, page, per_page), None
    
    async def _search_via_public_api(
        self,
        query: str,
        search_type: str,
        page: int,
        per_page: int,
    ) -> Tuple[Optional[SearchResult], Optional[str]]:
        """Try searching via the public REST API."""
        
        # Build query based on search type
        if search_type == "title":
            q_json = json.dumps({"title": {"-like": f"%{query}%"}})
        elif search_type == "author":
            q_json = json.dumps({"author": {"-like": f"%{query}%"}})
        elif search_type == "isbn":
            q_json = json.dumps({"isbn": {"-like": f"%{query}%"}})
        else:
            # Keyword search
            q_json = json.dumps([
                {"title": {"-like": f"%{query}%"}},
                {"author": {"-like": f"%{query}%"}},
            ])
        
        params = {
            "q": q_json,
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
    
    async def _search_via_svc(
        self,
        query: str,
        search_type: str,
        page: int,
        per_page: int,
    ) -> Tuple[Optional[SearchResult], Optional[str]]:
        """
        Search via the OPAC search endpoint.
        This uses the same search engine as the Koha web OPAC.
        Returns HTML which we parse for results.
        """
        if not self._client:
            return None, "Client not initialized"
        
        # Build the search URL - this is the OPAC search
        base_url = self.config.base_url.rstrip('/')
        
        # Map search type to Koha search index
        idx_map = {
            "title": "ti",
            "author": "au", 
            "subject": "su",
            "isbn": "nb",
            "keyword": "kw",
            "series": "se",
            "callnumber": "callnum",
        }
        idx = idx_map.get(search_type, "kw")
        
        # OPAC search URL
        search_url = f"{base_url}/cgi-bin/koha/opac-search.pl"
        params = {
            "idx": idx,
            "q": query,
            "offset": (page - 1) * per_page,
            "count": per_page,
        }
        
        logger.debug(f"OPAC search URL: {search_url} params: {params}")
        
        try:
            response = await self._client.get(search_url, params=params)
            logger.debug(f"OPAC search response: {response.status_code}, length: {len(response.text)}")
            
            if response.status_code == 200:
                html = response.text
                logger.debug(f"Got HTML response, length={len(html)}")
                logger.debug(f"HTML contains 'title_summary': {'title_summary' in html}")
                logger.debug(f"HTML contains 'numresults': {'numresults' in html}")
                result = self._parse_opac_html_results(html, page, per_page)
                logger.debug(f"Parsed {len(result.records)} records, total={result.total_count}")
                return result, None
            else:
                logger.debug(f"OPAC search returned status {response.status_code}")
                    
        except Exception as e:
            logger.debug(f"OPAC search failed: {e}")
            return None, str(e)
        
        return None, None
    
    def _parse_opac_html_results(
        self, 
        html: str,
        page: int,
        per_page: int
    ) -> SearchResult:
        """Parse OPAC search HTML results."""
        import re
        
        records = []
        total = 0
        
        # Extract total count - "Your search returned 2 results."
        total_match = re.search(r'returned\s+(\d+)\s+results?', html, re.IGNORECASE)
        if total_match:
            total = int(total_match.group(1))
        
        # Find all result rows - each has id="title_summary_X" where X is biblionumber
        # Pattern: <div id="title_summary_3" class="title_summary">
        title_summary_pattern = re.compile(
            r'<div\s+id="title_summary_(\d+)"[^>]*class="title_summary"[^>]*>(.*?)</div>\s*</td>',
            re.IGNORECASE | re.DOTALL
        )
        
        for match in title_summary_pattern.finditer(html):
            biblio_id = int(match.group(1))
            block = match.group(2)
            
            # Extract title from <a ... class="title">TITLE</a>
            title = ""
            title_match = re.search(
                r'<a[^>]*class="title"[^>]*>([^<]+)',
                block, re.IGNORECASE
            )
            if title_match:
                title = title_match.group(1).strip()
                # Clean up the title - remove trailing punctuation like " :"
                title = re.sub(r'\s*[:/]\s*$', '', title)
            
            # Extract author/responsibility from <span class="title_resp_stmt">
            author = ""
            author_match = re.search(
                r'<span\s+class="title_resp_stmt"[^>]*>([^<]+)',
                block, re.IGNORECASE
            )
            if author_match:
                author = author_match.group(1).strip()
                # Clean up - remove trailing periods and whitespace
                author = re.sub(r'[\s.]+$', '', author)
                # Remove leading "by " prefix if present
                author = re.sub(r'^by\s+', '', author, flags=re.IGNORECASE)
            
            # Extract publication year from <span ... class="publisher_date">1988</span>
            pub_year = None
            year_match = re.search(
                r'class="publisher_date"[^>]*>(\d{4})',
                block, re.IGNORECASE
            )
            if year_match:
                pub_year = year_match.group(1)
            
            # Extract publisher from <span ... class="publisher_name">
            publisher = ""
            pub_match = re.search(
                r'class="publisher_name"[^>]*>([^<]+)',
                block, re.IGNORECASE
            )
            if pub_match:
                publisher = pub_match.group(1).strip()
                publisher = re.sub(r'[,\s]+$', '', publisher)
            
            record = BiblioRecord(
                biblio_id=biblio_id,
                title=title or f"Record #{biblio_id}",
                author=author,
                publication_year=pub_year,
                publisher=publisher,
                raw_data={"biblionumber": biblio_id, "source": "opac_html"},
            )
            records.append(record)
        
        # If the title_summary pattern didn't work, try a simpler approach
        if not records:
            # Look for checkbox inputs with biblionumber values
            # <input type="checkbox" ... name="biblionumber" value="3" aria-label="Select search result: Occam 2 :" />
            checkbox_pattern = re.compile(
                r'<input[^>]*name="biblionumber"[^>]*value="(\d+)"[^>]*aria-label="Select search result:\s*([^"]*)"',
                re.IGNORECASE
            )
            
            for match in checkbox_pattern.finditer(html):
                biblio_id = int(match.group(1))
                title = match.group(2).strip()
                # Clean up title
                title = re.sub(r'\s*[:/]\s*$', '', title)
                
                record = BiblioRecord(
                    biblio_id=biblio_id,
                    title=title or f"Record #{biblio_id}",
                    raw_data={"biblionumber": biblio_id, "source": "opac_html"},
                )
                records.append(record)
        
        if not total:
            total = len(records)
        
        logger.debug(f"Parsed {len(records)} records from HTML, total={total}")
        logger.info(f"OPAC search found {len(records)} records (total: {total})")
        
        return SearchResult(records, total, page, per_page)
    
    def _parse_opac_search_results(
        self, 
        data: Dict[str, Any],
        page: int,
        per_page: int
    ) -> SearchResult:
        """Parse OPAC search JSON results (if available)."""
        records = []
        total = data.get("total", 0)
        
        for item in data.get("results", []):
            record = BiblioRecord(
                biblio_id=item.get("biblionumber", 0),
                title=item.get("title", ""),
                author=item.get("author", ""),
                publication_year=item.get("publicationyear") or item.get("copyrightdate"),
                publisher=item.get("publisher", ""),
                isbn=item.get("isbn", ""),
                item_type=item.get("itemtype", ""),
                call_number=item.get("callnumber", ""),
                summary=item.get("abstract", ""),
                raw_data=item,
            )
            records.append(record)
        
        return SearchResult(records, total, page, per_page)
    
    async def get_biblio(self, biblio_id: int) -> Tuple[Optional[BiblioRecord], Optional[str]]:
        """Get a single bibliographic record by ID."""
        logger.debug(f"get_biblio called for biblio_id={biblio_id}")
        
        # Try the public API with marc-in-json format
        data, error = await self._get_biblio_marcjson(biblio_id)
        
        if data and not error:
            logger.debug(f"Got biblio from API: {data.title}")
            return data, None
        
        logger.debug(f"API failed for biblio {biblio_id}: {error}, trying OPAC page")
        # Fall back to parsing the OPAC detail page
        return await self._get_biblio_from_opac(biblio_id)
    
    async def _get_biblio_marcjson(self, biblio_id: int) -> Tuple[Optional[BiblioRecord], Optional[str]]:
        """Get biblio details via the public API with marc-in-json format."""
        if not self._client:
            return None, "Client not initialized"
        
        url = f"{self.config.public_api_url}/biblios/{biblio_id}"
        headers = {
            "Accept": "application/marc-in-json",
        }
        
        logger.debug(f"Fetching biblio from {url}")
        
        try:
            response = await self._client.get(url, headers=headers)
            logger.debug(f"Biblio API response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_marc_in_json(biblio_id, data), None
            elif response.status_code == 404:
                return None, "Record not found"
            else:
                return None, f"API error: {response.status_code}"
                
        except Exception as e:
            logger.exception(f"Failed to get biblio {biblio_id}")
            return None, str(e)
    
    def _parse_marc_in_json(self, biblio_id: int, data: Dict[str, Any]) -> BiblioRecord:
        """Parse MARC-in-JSON format into BiblioRecord."""
        # MARC-in-JSON has 'fields' array with MARC field objects
        fields = data.get("fields", [])
        
        def get_field(tag: str, subfield: str = "a") -> str:
            """Extract a subfield from MARC fields."""
            for field in fields:
                if tag in field:
                    field_data = field[tag]
                    if isinstance(field_data, str):
                        return field_data
                    elif isinstance(field_data, dict):
                        subfields = field_data.get("subfields", [])
                        for sf in subfields:
                            if subfield in sf:
                                return sf[subfield]
            return ""
        
        def get_all_subfields(tag: str, subfield: str = "a") -> List[str]:
            """Extract all occurrences of a subfield."""
            results = []
            for field in fields:
                if tag in field:
                    field_data = field[tag]
                    if isinstance(field_data, dict):
                        subfields = field_data.get("subfields", [])
                        for sf in subfields:
                            if subfield in sf:
                                results.append(sf[subfield])
            return results
        
        # Extract common MARC fields
        # 245 = Title
        title = get_field("245", "a")
        subtitle = get_field("245", "b")
        if subtitle:
            title = f"{title} {subtitle}".strip()
        
        # 100/110 = Author
        author = get_field("100", "a") or get_field("110", "a") or get_field("700", "a")
        
        # 260/264 = Publication info
        publisher = get_field("260", "b") or get_field("264", "b")
        pub_place = get_field("260", "a") or get_field("264", "a")
        pub_year = get_field("260", "c") or get_field("264", "c")
        # Clean up year - extract just digits
        if pub_year:
            import re
            year_match = re.search(r'(\d{4})', pub_year)
            if year_match:
                pub_year = year_match.group(1)
        
        # 020 = ISBN
        isbn = get_field("020", "a")
        
        # 050 = Library of Congress Classification
        call_number_lcc = get_field("050", "a")
        lcc_cutter = get_field("050", "b")
        if lcc_cutter:
            call_number_lcc = f"{call_number_lcc} {lcc_cutter}".strip()
        
        # 082 = Dewey Decimal Classification
        call_number_dewey = get_field("082", "a")
        
        # 090 = Local call number (fallback for LOC)
        if not call_number_lcc:
            call_number_lcc = get_field("090", "a")
            lcc_cutter_90 = get_field("090", "b")
            if lcc_cutter_90:
                call_number_lcc = f"{call_number_lcc} {lcc_cutter_90}".strip()
        
        # Combined call number for backward compatibility
        call_number = call_number_lcc or call_number_dewey
        
        # 300 = Physical description
        physical_desc = get_field("300", "a")
        
        # 520 = Summary
        summary = get_field("520", "a")
        
        # 650 = Subjects
        subjects = get_all_subfields("650", "a")
        
        # Combine publisher info
        full_publisher = ""
        if pub_place:
            full_publisher = pub_place.rstrip(" :,")
        if publisher:
            if full_publisher:
                full_publisher += ": "
            full_publisher += publisher.rstrip(" ,")
        
        return BiblioRecord(
            biblio_id=biblio_id,
            title=title.rstrip(" /") or f"Record #{biblio_id}",
            author=author.rstrip(" ,"),
            publication_year=pub_year,
            publisher=full_publisher,
            isbn=isbn,
            call_number=call_number,
            call_number_lcc=call_number_lcc,
            call_number_dewey=call_number_dewey,
            physical_description=physical_desc,
            summary=summary,
            subjects=subjects,
            raw_data=data,
        )
    
    async def _get_biblio_from_opac(self, biblio_id: int) -> Tuple[Optional[BiblioRecord], Optional[str]]:
        """Get biblio details by parsing the OPAC detail page."""
        import re
        
        if not self._client:
            return None, "Client not initialized"
        
        base_url = self.config.base_url.rstrip('/')
        url = f"{base_url}/cgi-bin/koha/opac-detail.pl?biblionumber={biblio_id}"
        
        try:
            response = await self._client.get(url)
            if response.status_code != 200:
                return None, f"HTTP {response.status_code}"
            
            html = response.text
            
            # Extract title - look for <title> tag or h1/h2 with title class
            title = ""
            title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
                # Remove " | Library Name" suffix if present
                title = re.sub(r'\s*[|›»]\s*.*$', '', title)
            
            # Look for more specific title element
            title_match2 = re.search(
                r'class=["\'][^"\']*title[^"\']*["\'][^>]*>([^<]+)',
                html, re.IGNORECASE
            )
            if title_match2:
                title = title_match2.group(1).strip()
            
            # Extract author
            author = ""
            author_match = re.search(
                r'class=["\'][^"\']*author[^"\']*["\'][^>]*>([^<]+)',
                html, re.IGNORECASE
            )
            if author_match:
                author = author_match.group(1).strip()
            
            # Extract publication year
            pub_year = None
            year_match = re.search(r'(?:published|copyright|date)[:\s]*(\d{4})', html, re.IGNORECASE)
            if not year_match:
                year_match = re.search(r'\b((?:19|20)\d{2})\b', html)
            if year_match:
                pub_year = year_match.group(1)
            
            # Extract publisher
            publisher = ""
            pub_match = re.search(r'(?:publisher|imprint)[:\s]*([^<\n]+)', html, re.IGNORECASE)
            if pub_match:
                publisher = pub_match.group(1).strip()
            
            # Extract ISBN
            isbn = ""
            isbn_match = re.search(r'(?:ISBN)[:\s]*([\d\-X]+)', html, re.IGNORECASE)
            if isbn_match:
                isbn = isbn_match.group(1).strip()
            
            # Extract call number
            call_number = ""
            call_match = re.search(r'(?:call\s*number|shelfmark)[:\s]*([^<\n]+)', html, re.IGNORECASE)
            if call_match:
                call_number = call_match.group(1).strip()
            
            record = BiblioRecord(
                biblio_id=biblio_id,
                title=title or f"Record #{biblio_id}",
                author=author,
                publication_year=pub_year,
                publisher=publisher,
                isbn=isbn,
                call_number=call_number,
                raw_data={"biblionumber": biblio_id, "source": "opac_html"},
            )
            
            return record, None
            
        except Exception as e:
            logger.exception(f"Failed to get biblio {biblio_id} from OPAC")
            return None, str(e)
    
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
            public_note=data.get("public_note", ""),
        )


# Singleton-ish access for the API client
_api_client: Optional[KohaAPIClient] = None


async def get_api_client(config: KohaConfig) -> KohaAPIClient:
    """Get or create the API client."""
    global _api_client
    if _api_client is None:
        _api_client = KohaAPIClient(config)
    return _api_client
