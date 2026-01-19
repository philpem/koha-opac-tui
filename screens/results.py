"""
Search Results Screen - Displays search results in a list format.
Inspired by the classic Dynix search results display.
"""

from datetime import datetime
from typing import List, Optional
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, Label, LoadingIndicator
from textual.binding import Binding

from api.client import KohaAPIClient, BiblioRecord, SearchResult
from utils.config import KohaConfig


class ResultItem(ListItem):
    """A search result list item."""
    
    def __init__(self, index: int, record: BiblioRecord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index
        self.record = record
    
    def compose(self) -> ComposeResult:
        # Format: "1. Author Name, Date\n    Title"
        author_info = self.record.author or "Unknown Author"
        if self.record.publication_year:
            author_info += f", {self.record.publication_year}"
        
        # Truncate title if too long
        title = self.record.title
        if len(title) > 60:
            title = title[:57] + "..."
        
        # Item type indicator
        item_type = ""
        if "sound" in (self.record.item_type or "").lower():
            item_type = "[sound recording] "
        elif "video" in (self.record.item_type or "").lower():
            item_type = "[video] "
        elif "dvd" in (self.record.item_type or "").lower():
            item_type = "[DVD] "
        
        year_display = self.record.publication_year or ""
        
        with Horizontal():
            yield Static(f"{self.index}.", classes="result-number")
            with Vertical():
                yield Static(f"{author_info}", classes="result-author")
                yield Static(f"    {item_type}{title}", classes="result-title")
            yield Static(year_display, classes="result-date")


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
        yield Static(self._get_header_text(), id="header", classes="header-bar")
        
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
        yield Static(self._get_status_text(), id="status-bar", classes="status-bar")
    
    def _get_header_text(self) -> str:
        """Generate the header bar text."""
        now = datetime.now()
        date_str = now.strftime("%d %b %Y").upper()
        time_str = now.strftime("%I:%M%p").lower()
        
        library_name = self.config.library_name.upper()
        
        left = f"  {date_str}"
        center = library_name
        right = f"{time_str}  "
        
        total_width = 80
        left_space = (total_width - len(center)) // 2 - len(left)
        right_space = total_width - len(left) - left_space - len(center) - len(right)
        
        return f"{left}{' ' * max(1, left_space)}{center}{' ' * max(1, right_space)}{right}\n{'Dial Pac':^80}"
    
    def _get_column_header(self) -> str:
        """Get the column header row."""
        return f"{'AUTHOR/TITLE':<66}{'DATE':>12}"
    
    def _get_status_text(self) -> str:
        """Generate the status bar text."""
        return (
            "Enter an item number for more detail :\n"
            "SO=Start Over, B=Back, SL=Sort List, ?=Help, <Enter>=Next Screen"
        )
    
    def on_mount(self) -> None:
        """Start loading results when mounted."""
        self.query_one("#loading", LoadingIndicator).display = True
        self.query_one("#results-list", ListView).display = False
        self._load_results()
    
    @work(exclusive=True)
    async def _load_results(self) -> None:
        """Load search results asynchronously."""
        self.is_loading = True
        
        results, error = await self.api_client.search_biblios(
            query=self.search_query,
            search_type=self.search_type,
            page=self.current_page,
            per_page=self.config.items_per_page,
        )
        
        # Update UI (we're back on the main thread after await)
        self._update_results(results, error)
    
    def _update_results(self, results: Optional[SearchResult], error: Optional[str]) -> None:
        """Update the UI with results."""
        self.is_loading = False
        self.query_one("#loading", LoadingIndicator).display = False
        
        results_list = self.query_one("#results-list", ListView)
        results_list.clear()
        
        if error:
            results_list.append(ListItem(Static(f"Error: {error}")))
            results_list.display = True
            return
        
        if not results or not results.records:
            results_list.append(ListItem(Static("No results found.")))
            results_list.display = True
            self._update_pagination(0, 0, 1)
            return
        
        self.results = results
        
        # Add result items
        for i, record in enumerate(results.records, start=1):
            results_list.append(ResultItem(i, record))
        
        results_list.display = True
        results_list.focus()
        
        # Update pagination info
        self._update_pagination(results.total_count, len(results.records), results.total_pages)
    
    def _update_pagination(self, total: int, shown: int, total_pages: int) -> None:
        """Update the pagination display."""
        pagination = self.query_one("#pagination-info", Static)
        if total == 0:
            pagination.update("No items found")
        else:
            pagination.update(
                f"** {total} Items - Page {self.current_page} of {total_pages} - "
                f"{'More on Next Screen' if self.current_page < total_pages else 'End of Results'} **"
            )
    
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
