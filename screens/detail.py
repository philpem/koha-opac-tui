"""
Item Detail Screen - Displays detailed bibliographic information and holdings.
Shows item details in the top half and holdings/availability in the bottom half.
"""

from typing import List, Optional
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static, DataTable, LoadingIndicator, Rule
from textual.binding import Binding

from api.client import KohaAPIClient, BiblioRecord, HoldingItem
from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar


class ItemDetailScreen(Screen):
    """
    Detailed view of a bibliographic record with holdings information.
    Upper half shows bibliographic details, lower half shows item holdings.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "go_back", "Back", show=False),
        Binding("q", "go_back", "Back", show=False),
        Binding("f1", "show_help", "Help"),
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
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Dial Pac",
            id="header"
        )
        
        with Container(id="main-content"):
            # Loading indicator
            yield LoadingIndicator(id="loading")
            
            # Bibliographic Details - compact single line title
            yield Static("BIBLIOGRAPHIC DETAILS", id="biblio-title", classes="section-title")
            yield Static("Loading...", id="biblio-details")
            
            # Holdings section
            yield Static("HOLDINGS", id="holdings-title", classes="section-title")
            yield DataTable(id="holdings-table")
            yield Static("", id="holdings-summary")
        
        # Status bar
        yield FooterBar(
            prompt="",
            shortcuts="F1=Help, Esc=Back to results",
            id="status-bar"
        )
    
    def on_mount(self) -> None:
        """Load the record details when mounted."""
        # Setup holdings table columns
        # Use configured terminology for call number
        call_label = self.config.get_call_number_label_short()
        
        table = self.query_one("#holdings-table", DataTable)
        table.add_columns(
            "Library",
            "Location",
            call_label,
            "Status",
            "Due Date",
            "Note",
        )
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Hide table until loaded
        table.display = False
        
        self._load_record()
    
    def _load_record(self) -> None:
        """Load record details asynchronously."""
        self._fetch_record()
    
    @work(exclusive=True)
    async def _fetch_record(self) -> None:
        """Fetch record and holdings from the API."""
        # First, get libraries to resolve names
        await self.api_client.get_libraries()
        
        # Fetch bibliographic record
        record, record_error = await self.api_client.get_biblio(self.biblio_id)
        
        # Fetch holdings
        holdings, holdings_error = await self.api_client.get_biblio_items(self.biblio_id)
        
        # Update UI (we're back on the main thread after await)
        self._update_display(record, record_error, holdings, holdings_error)
    
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
                
                # Truncate public note if too long
                note = item.public_note or "-"
                if len(note) > 20:
                    note = note[:17] + "..."
                
                table.add_row(
                    item.library_name or item.library_id,
                    item.location or "-",
                    item.call_number or "-",
                    status_text,
                    item.due_date or "-",
                    note,
                )
            
            # Calculate summary
            total = len(holdings)
            available = sum(1 for h in holdings if h.is_available)
            on_loan = sum(1 for h in holdings if h.status == "On Loan")
            
            summary.update(
                f"Total copies: {total} | Available: {available} | On loan: {on_loan}"
            )
            
            table.display = True
            table.focus()
        else:
            summary.update("No copies available in the system.")
    
    def _format_biblio_details(self, record: BiblioRecord) -> str:
        """Format bibliographic record for display - compact for 80x25."""
        lines = []
        
        # Title (prominent) - may wrap
        title = record.title or "Unknown Title"
        lines.append(f"Title:     {title}")
        
        # Author
        if record.author:
            lines.append(f"Author:    {record.author}")
        
        # Publication info on one line
        pub_parts = []
        if record.publisher:
            pub_parts.append(record.publisher)
        if record.publication_year:
            pub_parts.append(record.publication_year)
        if pub_parts:
            lines.append(f"Published: {', '.join(pub_parts)}")
        
        # ISBN on its own line if it exists
        if record.isbn:
            lines.append(f"ISBN:      {record.isbn}")
        
        # Call Number(s) based on display settings
        call_label = self.config.get_call_number_label()
        display_mode = self.config.call_number_display
        
        if display_mode == "both":
            # Show both LOC and Dewey on separate lines if both exist
            if record.call_number_lcc:
                lines.append(f"LOC {call_label}: {record.call_number_lcc}")
            if record.call_number_dewey:
                lines.append(f"Dewey {call_label}: {record.call_number_dewey}")
            # Fallback to generic call number if neither specific one exists
            if not record.call_number_lcc and not record.call_number_dewey and record.call_number:
                lines.append(f"{call_label}: {record.call_number}")
        elif display_mode == "lcc":
            cn = record.call_number_lcc or record.call_number
            if cn:
                lines.append(f"{call_label}: {cn}")
        elif display_mode == "dewey":
            cn = record.call_number_dewey or record.call_number
            if cn:
                lines.append(f"{call_label}: {cn}")
        
        # Summary - truncate if too long
        if record.summary:
            summary = record.summary
            if len(summary) > 150:
                summary = summary[:147] + "..."
            lines.append(f"Summary:   {summary}")
        
        return "\n".join(lines)
    
    def action_go_back(self) -> None:
        """Go back to results screen."""
        self.app.pop_screen()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "detail"})
