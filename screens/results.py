"""
Search Results Screen - Displays search results in a list format.
Inspired by the classic Dynix search results display.
"""

from typing import List, Optional
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, LoadingIndicator
from textual.binding import Binding

from api.client import KohaAPIClient, BiblioRecord, SearchResult
from utils.config import KohaConfig
from utils.logging import get_logger
from widgets import HeaderBar, FooterBar

# Display formatting constants
RESULT_LINE_WIDTH = 71  # Character width for result display (leaving room for margins/scrollbar)
RESULT_INDEX_YEAR_WIDTH = 10  # Width reserved for "NNN. " (5) and " YEAR" (4) with spacing (1)
RESULT_TITLE_INDENT = 5  # Character indent for title line
ELLIPSIS = "..."  # Truncation indicator text
RESULT_YEAR_WIDTH = 4  # Width for year display (e.g., "2024")
RESULT_LINES_PER_ITEM_SPACED = 3  # Lines per result item with spacing enabled
RESULT_LINES_PER_ITEM_COMPACT = 2  # Lines per result item without spacing
DEFAULT_VISIBLE_ITEMS_FALLBACK = 5  # Default visible items if height calculation fails

# Get logger from centralized logging module
logger = get_logger(__name__)


class ResultItem(ListItem):
    """A search result list item."""

    def __init__(self, index: int, record: BiblioRecord, spaced: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.record = record
        self.spaced = spaced
    
    def compose(self) -> ComposeResult:
        author = self.record.author or "Unknown"
        # Truncate author if needed - leave room for index and year
        max_author = RESULT_LINE_WIDTH - RESULT_INDEX_YEAR_WIDTH
        if len(author) > max_author:
            author = author[:max_author - len(ELLIPSIS)] + ELLIPSIS

        title = self.record.title
        # Truncate title - leave room for indent
        max_title = RESULT_LINE_WIDTH - RESULT_TITLE_INDENT
        if len(title) > max_title:
            title = title[:max_title - len(ELLIPSIS)] + ELLIPSIS
        
        # Item type indicator (short)
        item_type = ""
        itype = (self.record.item_type or "").lower()
        if "sound" in itype:
            item_type = "[CD] "
        elif "video" in itype or "dvd" in itype:
            item_type = "[DVD] "
        
        year = self.record.publication_year or ""
        if len(year) > RESULT_YEAR_WIDTH:
            year = year[:RESULT_YEAR_WIDTH]

        # Format using fixed-width fields
        # Line 1: "NNN. Author                                           YEAR"
        # Line 2: "     Title"
        author_width = RESULT_LINE_WIDTH - RESULT_INDEX_YEAR_WIDTH
        line1 = f"{self.index:3d}. {author:<{author_width}} {year:>RESULT_YEAR_WIDTH}"
        line2 = f"     {item_type}{title}"
        
        content = f"{line1}\n{line2}"
        if self.spaced:
            content += "\n"  # Add blank line for spacing
        
        yield Static(content, classes="result-item-text")


class SearchResultsScreen(Screen):
    """
    Search results display screen.
    Shows a paginated list of search results.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back", show=False),
        Binding("enter", "select_item", "Select", show=False),
        Binding("n", "next_page", "Next Page", show=False),
        Binding("p", "prev_page", "Previous Page", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("home", "go_home", "Home", show=False),
        Binding("end", "go_end", "End", show=False),
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
            # Search info with blank lines before and after
            yield Static(
                f"\nYour Search: {self.search_query}\n",
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
            
            # Pagination info with blank lines before and after
            yield Static("", id="pagination-info", classes="pagination-info")
        
        # Status bar
        yield FooterBar(
            prompt="",
            shortcuts="1-9,0=Select, F1=Help, Esc=Back",
            id="status-bar"
        )
    
    def _get_column_header(self) -> str:
        """Get the column header row - aligned with result items."""
        # Format: "NNN. AUTHOR...                                        YEAR"
        author_width = RESULT_LINE_WIDTH - RESULT_INDEX_YEAR_WIDTH
        return f"{'#':>3}  {'AUTHOR / TITLE':<{author_width}} {'YEAR':>RESULT_YEAR_WIDTH}"
    
    def on_mount(self) -> None:
        """Start loading results when mounted."""
        logger.debug(f"SearchResultsScreen mounted, query='{self.search_query}', type='{self.search_type}'")
        self.query_one("#loading", LoadingIndicator).display = True
        self.query_one("#results-list", ListView).display = False
        self._load_results()
    
    def on_resize(self, event) -> None:
        """Handle terminal resize."""
        pass  # Height is fixed in CSS
    
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
            self._show_no_results_message(f"Error: {error}")
            return
        
        if not results or not results.records:
            logger.debug("No results to display")
            self._show_no_results_message("No results found for your search.")
            return
        
        # If only one result, go directly to detail screen
        if len(results.records) == 1 and results.total_count == 1:
            logger.debug("Single result - going directly to detail screen")
            record = results.records[0]
            # Replace this screen with the detail screen (don't push, replace)
            self.app.pop_screen()
            self.app.push_screen(
                "detail",
                {"biblio_id": record.biblio_id}
            )
            return
        
        logger.debug(f"Displaying {len(results.records)} results")
        self.results = results
        
        # Add result items with optional spacing
        spaced = self.config.result_spacing
        for i, record in enumerate(results.records, start=1):
            results_list.append(ResultItem(i, record, spaced=spaced))
        
        results_list.display = True
        results_list.focus()
        
        # Select the first item
        if results_list.children:
            results_list.index = 0
        
        # Update pagination info
        self._update_pagination(results.total_count, len(results.records), results.total_pages)
    
    def _show_no_results_message(self, message: str) -> None:
        """Show a no results message with option to go back."""
        results_list = self.query_one("#results-list", ListView)
        pagination = self.query_one("#pagination-info", Static)
        column_header = self.query_one("#column-header", Static)
        
        # Hide the column header for no results
        column_header.display = False
        
        # Show message in list area
        results_list.append(ListItem(Static(f"\n{message}\n\nPress Esc or Enter to search again.")))
        results_list.display = True
        
        # Clear pagination
        pagination.update("")
    
    def _update_pagination(self, total: int, shown: int, total_pages: int) -> None:
        """Update the pagination display."""
        pagination = self.query_one("#pagination-info", Static)
        if total == 0:
            pagination.update("\nNo items found\n")
        elif total > shown:
            pagination.update(f"\n** Too many results ({total}) - first {shown} shown - Use arrow keys to scroll **\n")
        else:
            pagination.update(f"\n** {total} Items - Use arrow keys to scroll **\n")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle result selection."""
        item = event.item
        if isinstance(item, ResultItem):
            self._show_detail(item.record)
        else:
            # If it's not a ResultItem (e.g., no results message), go back
            self.action_go_back()
    
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
    
    def on_key(self, event) -> None:
        """Handle key events - intercept before ListView processes them."""
        if event.key == "pagedown":
            self.action_page_down()
            event.prevent_default()
            event.stop()
        elif event.key == "pageup":
            self.action_page_up()
            event.prevent_default()
            event.stop()
        elif event.key == "home":
            self.action_go_home()
            event.prevent_default()
            event.stop()
        elif event.key == "end":
            self.action_go_end()
            event.prevent_default()
            event.stop()
    
    def _get_visible_items_count(self) -> int:
        """Calculate how many items are visible based on list height."""
        results_list = self.query_one("#results-list", ListView)
        list_height = results_list.size.height
        if list_height > 0:
            # Each item is 2 lines (author + title), or 3 if spaced
            lines_per_item = RESULT_LINES_PER_ITEM_SPACED if self.config.result_spacing else RESULT_LINES_PER_ITEM_COMPACT
            return max(1, (list_height // lines_per_item) - 1)
        return DEFAULT_VISIBLE_ITEMS_FALLBACK
    
    def action_page_down(self) -> None:
        """Move cursor down by a page worth of items."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.children:
            visible_count = self._get_visible_items_count()
            current = results_list.index or 0
            new_index = min(current + visible_count, len(results_list.children) - 1)
            results_list.index = new_index
    
    def action_page_up(self) -> None:
        """Move cursor up by a page worth of items."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.children:
            visible_count = self._get_visible_items_count()
            current = results_list.index or 0
            new_index = max(current - visible_count, 0)
            results_list.index = new_index
    
    def action_go_home(self) -> None:
        """Move cursor to the first item."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.children:
            results_list.index = 0
    
    def action_go_end(self) -> None:
        """Move cursor to the last item."""
        results_list = self.query_one("#results-list", ListView)
        if results_list.children:
            results_list.index = len(results_list.children) - 1
    
    def action_next_page(self) -> None:
        """Go to next page of results (legacy - now same as page_down)."""
        self.action_page_down()
    
    def action_prev_page(self) -> None:
        """Go to previous page of results (legacy - now same as page_up)."""
        self.action_page_up()
    
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
