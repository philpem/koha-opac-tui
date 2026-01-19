"""
Item Detail Screen - Displays detailed bibliographic information and holdings.
Shows item details in the top half and holdings/availability in the bottom half.
"""

from datetime import datetime
from typing import List, Optional
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static, DataTable, LoadingIndicator, Rule
from textual.binding import Binding
from textual.worker import Worker, get_current_worker

from api.client import KohaAPIClient, BiblioRecord, HoldingItem
from utils.config import KohaConfig


class ItemDetailScreen(Screen):
    """
    Detailed view of a bibliographic record with holdings information.
    Upper half shows bibliographic details, lower half shows item holdings.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back", show=False),
        Binding("q", "go_back", "Back", show=False),
    ]
    
    def __init__(
        self,
        config: KohaConfig,
        api_client: KohaAPIClient,
        biblio_id: int,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = config
        self.api_client = api_client
        self.biblio_id = biblio_id
        self.record: Optional[BiblioRecord] = None
        self.holdings: List[HoldingItem] = []
    
    def compose(self) -> ComposeResult:
        """Compose the detail screen layout."""
        # Header bar
        yield Static(self._get_header_text(), id="header", classes="header-bar")
        
        with Container(id="main-content"):
            # Loading indicator
            yield LoadingIndicator(id="loading")
            
            # Upper section - Bibliographic Details
            with ScrollableContainer(id="biblio-section"):
                yield Static("── BIBLIOGRAPHIC DETAILS ──", classes="box-title")
                with Container(id="detail-container", classes="content-box"):
                    yield Static("Loading...", id="biblio-details")
            
            # Divider
            yield Rule(line_style="heavy")
            
            # Lower section - Holdings Information
            with Container(id="holdings-section"):
                yield Static("── ITEM HOLDINGS ──", classes="box-title")
                yield DataTable(id="holdings-table")
                yield Static("", id="holdings-summary")
        
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
    
    def _get_status_text(self) -> str:
        """Generate the status bar text."""
        return (
            "B=Back to results, ?=Help\n"
            "Use arrow keys to scroll through holdings"
        )
    
    def on_mount(self) -> None:
        """Load the record details when mounted."""
        # Setup holdings table columns
        table = self.query_one("#holdings-table", DataTable)
        table.add_columns(
            "Library",
            "Location",
            "Call Number",
            "Status",
            "Due Date",
        )
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Hide table until loaded
        table.display = False
        
        self._load_record()
    
    def _load_record(self) -> None:
        """Load record details asynchronously."""
        self.run_worker(self._fetch_record(), exclusive=True)
    
    async def _fetch_record(self) -> None:
        """Fetch record and holdings from the API."""
        worker = get_current_worker()
        
        # First, get libraries to resolve names
        await self.api_client.get_libraries()
        
        # Fetch bibliographic record
        record, record_error = await self.api_client.get_biblio(self.biblio_id)
        
        # Fetch holdings
        holdings, holdings_error = await self.api_client.get_biblio_items(self.biblio_id)
        
        if not worker.is_cancelled:
            self.call_from_thread(
                self._update_display,
                record,
                record_error,
                holdings,
                holdings_error
            )
    
    def _update_display(
        self,
        record: Optional[BiblioRecord],
        record_error: Optional[str],
        holdings: List[HoldingItem],
        holdings_error: Optional[str]
    ) -> None:
        """Update the display with fetched data."""
        self.query_one("#loading", LoadingIndicator).display = False
        
        # Update bibliographic details
        details_widget = self.query_one("#biblio-details", Static)
        
        if record_error:
            details_widget.update(f"Error loading record: {record_error}")
        elif record:
            self.record = record
            details_widget.update(self._format_biblio_details(record))
        else:
            details_widget.update("Record not found.")
        
        # Update holdings table
        table = self.query_one("#holdings-table", DataTable)
        summary = self.query_one("#holdings-summary", Static)
        
        if holdings_error:
            summary.update(f"Error loading holdings: {holdings_error}")
        elif holdings:
            self.holdings = holdings
            
            for item in holdings:
                # Determine style based on availability
                status_text = item.status
                
                table.add_row(
                    item.library_name or item.library_id,
                    item.location or "-",
                    item.call_number or "-",
                    status_text,
                    item.due_date or "-",
                )
            
            # Calculate summary
            total = len(holdings)
            available = sum(1 for h in holdings if h.is_available)
            on_loan = sum(1 for h in holdings if h.status == "On Loan")
            
            summary.update(
                f"\nTotal copies: {total} | Available: {available} | On loan: {on_loan}"
            )
            
            table.display = True
            table.focus()
        else:
            summary.update("No copies available in the system.")
    
    def _format_biblio_details(self, record: BiblioRecord) -> str:
        """Format bibliographic record for display."""
        lines = []
        
        # Title (prominent)
        title = record.title or "Unknown Title"
        lines.append(f"Title:          {title}")
        lines.append("")
        
        # Author
        if record.author:
            lines.append(f"Author:         {record.author}")
        
        # Publication info
        pub_info = []
        if record.publisher:
            pub_info.append(record.publisher)
        if record.publication_year:
            pub_info.append(record.publication_year)
        if pub_info:
            lines.append(f"Published:      {', '.join(pub_info)}")
        
        # Edition
        if record.edition:
            lines.append(f"Edition:        {record.edition}")
        
        # Physical description
        if record.physical_description:
            lines.append(f"Description:    {record.physical_description}")
        
        # ISBN
        if record.isbn:
            lines.append(f"ISBN:           {record.isbn}")
        
        # Call number
        if record.call_number:
            lines.append(f"Call Number:    {record.call_number}")
        
        # Item type
        if record.item_type:
            lines.append(f"Material Type:  {record.item_type}")
        
        # Series
        if record.series:
            lines.append(f"Series:         {record.series}")
        
        # Subjects
        if record.subjects:
            lines.append(f"Subjects:       {'; '.join(record.subjects)}")
        
        # Summary/abstract
        if record.summary:
            lines.append("")
            lines.append("Summary:")
            # Word wrap the summary
            summary_lines = self._wrap_text(record.summary, 70)
            for line in summary_lines:
                lines.append(f"  {line}")
        
        # Notes
        if record.notes:
            lines.append("")
            lines.append(f"Notes:          {record.notes}")
        
        return "\n".join(lines)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Simple word wrapping."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def action_go_back(self) -> None:
        """Go back to results screen."""
        self.app.pop_screen()
