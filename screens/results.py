"""
Search Results Screen - Displays search results in a list format.
Inspired by the classic Dynix search results display.
"""

import logging
from typing import List, Optional
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, LoadingIndicator
from textual.binding import Binding

from api.client import KohaAPIClient, BiblioRecord, SearchResult
from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar

# Set up file-based logging
logger = logging.getLogger(__name__)
_debug_handler = logging.FileHandler('/tmp/koha_tui_debug.log')
_debug_handler.setLevel(logging.DEBUG)
_debug_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_debug_handler)
logger.setLevel(logging.DEBUG)


class ResultItem(ListItem):
    """A search result list item."""
    
    def __init__(self, index: int, record: BiblioRecord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.record = record
    
    def compose(self) -> ComposeResult:
        # Format to fit 74 chars max (leaving room for margins/scrollbar)
        author = self.record.author or "Unknown"
        # Truncate author if needed
        if len(author) > 28:
            author = author[:25] + "..."
        
        # Truncate title if too long  
        title = self.record.title
        if len(title) > 40:
            title = title[:37] + "..."
        
        # Item type indicator (short)
        item_type = ""
        itype = (self.record.item_type or "").lower()
        if "sound" in itype:
            item_type = "[CD] "
        elif "video" in itype or "dvd" in itype:
            item_type = "[DVD] "
        
        year = self.record.publication_year or ""
        if len(year) > 4:
            year = year[:4]
        
        # Line 1: "1. Author Name                    YEAR"
        # Line 2: "    Title"
        # Keep under 74 chars
        line1 = f"{self.index:2d}. {author}"
        line2 = f"    {item_type}{title}"
        
        # Add year right-aligned, total max 72 chars
        if year:
            padding = 68 - len(line1)
            if padding > 0:
                line1 = line1 + " " * padding + year
        
        yield Static(f"{line1}\n{line2}", classes="result-item-text")


class SearchResultsScreen(Screen):
    """
    Search results display screen.
    Shows a paginated list of search results.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back", show=False),
        Binding("enter", "select_item", "Select", show=False),
        Binding("n", "next_page", "Next Page"),
        Binding("p", "prev_page", "Previous Page"),
        Binding("pagedown", "next_page", "Next Page", show=False),
        Binding("pageup", "prev_page", "Previous Page", show=False),
        Binding("f1", "show_help", "Help"),
        Binding("1", "select_1", show=False),
        Binding("2", "select_2", show=False),
        Binding("3", "select_3", show=False),
        Binding("4", "select_4", show=False),
        Binding("5", "select_5", show=False),
        Binding("6", "select_6", show=False),
        Binding("7", "select_7", show=False),
        Binding("8", "select_8", show=False),
        Binding("9", "select_9", show=False),
        Binding("0", "select_10", show=False),
    ]
    
    def __init__(
        self,
        config: KohaConfig,
        api_client: KohaAPIClient,
        query: str,
        search_type: str = "title",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = config
        self.api_client = api_client
        self.search_query = query  # Renamed to avoid shadowing Screen.query
        self.search_type = search_type
        self.current_page = 1
        self.results: Optional[SearchResult] = None
        self.is_loading = False
    
    def compose(self) -> ComposeResult:
        """Compose the results screen layout."""
        # Header bar
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Dial Pac",
            id="header"
        )
        
        with Container(id="main-content"):
            # Search info
            yield Static(
                f"Your Search: {self.search_query}",
                id="search-info"
            )
            
            # Column headers
            yield Static(
                self._get_column_header(),
                id="column-header",
                classes="holdings-header"
            )
            
            # Results list
            yield ListView(id="results-list")
            
            # Loading indicator
            yield LoadingIndicator(id="loading")
            
            # Pagination info
            yield Static("", id="pagination-info", classes="pagination-info")
        
        # Status bar
        yield FooterBar(
            prompt="",
            shortcuts="1-9,0=Select, F1=Help, Esc=Back",
            id="status-bar"
        )
    
    def _get_column_header(self) -> str:
        """Get the column header row - fits in 72 chars."""
        return f"{'#':<4}{'AUTHOR / TITLE':<60}{'YEAR':>8}"
    
    def on_mount(self) -> None:
        """Start loading results when mounted."""
        logger.debug(f"SearchResultsScreen mounted, query='{self.search_query}', type='{self.search_type}'")
        self.query_one("#loading", LoadingIndicator).display = True
        self.query_one("#results-list", ListView).display = False
        self._load_results()
    
    @work(exclusive=True)
    async def _load_results(self) -> None:
        """Load search results asynchronously."""
        logger.debug(f"_load_results called, query='{self.search_query}'")
        logger.debug(f"api_client type: {type(self.api_client).__name__}")
        logger.debug(f"api_client config base_url: {self.api_client.config.base_url}")
        self.is_loading = True
        
        # Load more results at once - let the list scroll
        logger.debug(f"Calling api_client.search_biblios...")
        results, error = await self.api_client.search_biblios(
            query=self.search_query,
            search_type=self.search_type,
            page=1,
            per_page=100,  # Load all at once, let list scroll
        )
        logger.debug(f"search_biblios returned: results={results}, error={error}")
        
        # Update UI (we're back on the main thread after await)
        self._update_results(results, error)
    
    def _update_results(self, results: Optional[SearchResult], error: Optional[str]) -> None:
        """Update the UI with results."""
        logger.debug(f"_update_results called: results={results}, error={error}")
        self.is_loading = False
        self.query_one("#loading", LoadingIndicator).display = False
        
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()
        
        if error:
            logger.debug(f"Displaying error: {error}")
            results_list.append(ListItem(Static(f"Error: {error}")))
            results_list.display = True
            return
        
        if not results or not results.records:
            logger.debug("No results to display")
            results_list.append(ListItem(Static("No results found.")))
            results_list.display = True
            self._update_pagination(0, 0, 1)
            return
        
        logger.debug(f"Displaying {len(results.records)} results")
        self.results = results
        
        # Add result items
        for i, record in enumerate(results.records, start=1):
            results_list.append(ResultItem(i, record))
        
        results_list.display = True
        results_list.focus()
        
        # Select the first item
        if results_list.children:
            results_list.index = 0
        
        # Update pagination info
        self._update_pagination(results.total_count, len(results.records), results.total_pages)
    
    def _update_pagination(self, total: int, shown: int, total_pages: int) -> None:
        """Update the pagination display."""
        pagination = self.query_one("#pagination-info", Static)
        if total == 0:
            pagination.update("No items found")
        else:
            pagination.update(f"** {total} Items - Use arrow keys to scroll **")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle result selection."""
        item = event.item
        if isinstance(item, ResultItem):
            self._show_detail(item.record)
    
    def _show_detail(self, record: BiblioRecord) -> None:
        """Navigate to the detail screen for a record."""
        self.app.push_screen(
            "detail",
            {"biblio_id": record.biblio_id}
        )
    
    def _select_by_number(self, num: int) -> None:
        """Select a result by its number."""
        if self.results and 1 <= num <= len(self.results.records):
            record = self.results.records[num - 1]
            self._show_detail(record)
    
    def action_go_back(self) -> None:
        """Go back to search screen."""
        self.app.pop_screen()
    
    def action_next_page(self) -> None:
        """Go to next page of results."""
        if self.results and self.results.has_next and not self.is_loading:
            self.current_page += 1
            self.query_one("#loading", LoadingIndicator).display = True
            self.query_one("#results-list", ListView).display = False
            self._load_results()
    
    def action_prev_page(self) -> None:
        """Go to previous page of results."""
        if self.results and self.results.has_prev and not self.is_loading:
            self.current_page -= 1
            self.query_one("#loading", LoadingIndicator).display = True
            self.query_one("#results-list", ListView).display = False
            self._load_results()
    
    def action_select_item(self) -> None:
        """Select the currently highlighted item."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.highlighted_child:
            item = results_list.highlighted_child
            if isinstance(item, ResultItem):
                self._show_detail(item.record)
    
    def action_select_1(self) -> None:
        self._select_by_number(1)
    
    def action_select_2(self) -> None:
        self._select_by_number(2)
    
    def action_select_3(self) -> None:
        self._select_by_number(3)
    
    def action_select_4(self) -> None:
        self._select_by_number(4)
    
    def action_select_5(self) -> None:
        self._select_by_number(5)
    
    def action_select_6(self) -> None:
        self._select_by_number(6)
    
    def action_select_7(self) -> None:
        self._select_by_number(7)
    
    def action_select_8(self) -> None:
        self._select_by_number(8)
    
    def action_select_9(self) -> None:
        self._select_by_number(9)
    
    def action_select_10(self) -> None:
        self._select_by_number(10)
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "results"})
