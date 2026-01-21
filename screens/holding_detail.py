"""
Holding Detail Screen - Displays detailed information about holdings at a specific library.
Shows bibliographic details and all holdings from the selected library.
"""

from typing import List, Optional
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static, DataTable
from textual.binding import Binding

from api.client import BiblioRecord, HoldingItem
from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar


class HoldingDetailScreen(Screen):
    """
    Detailed view of holdings at a specific library.
    Shows bibliographic info and all copies held by that library.
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
        record: Optional[BiblioRecord],
        holdings: List[HoldingItem],
        selected_holding: Optional[HoldingItem] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = config
        self.record = record
        self.holdings = holdings
        self.selected_holding = selected_holding
    
    def compose(self) -> ComposeResult:
        """Compose the holding detail screen layout."""
        # Determine library name for header
        library_name = "Unknown Library"
        if self.holdings:
            library_name = self.holdings[0].library_name or self.holdings[0].library_id
        
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Dial Pac",
            id="header"
        )
        
        with Container(id="main-content"):
            with ScrollableContainer(id="holding-scroll"):
                # Bibliographic Details section
                yield Static("BIBLIOGRAPHIC DETAILS", id="biblio-title", classes="section-title")
                yield Static(self._format_biblio_details(), id="biblio-details")
                
                # Library Holdings section
                yield Static(f"HOLDINGS AT: {library_name}", id="library-title", classes="section-title")
                yield DataTable(id="holdings-table")
                
                # Item Details section (for selected holding)
                yield Static("ITEM DETAILS", id="item-title", classes="section-title")
                yield Static(self._format_item_details(), id="item-details")
        
        yield FooterBar(
            prompt="",
            shortcuts="F1=Help, Esc=Back to record",
            id="status-bar"
        )
    
    def on_mount(self) -> None:
        """Set up the holdings table on mount."""
        call_label = self.config.get_call_number_label_short()
        
        table = self.query_one("#holdings-table", DataTable)
        table.add_columns(
            "Copy",
            "Location",
            call_label,
            "Barcode",
            "Status",
            "Due Date",
        )
        table.cursor_type = "row"
        table.zebra_stripes = True
        
        # Populate table with holdings
        for i, item in enumerate(self.holdings, start=1):
            table.add_row(
                str(item.copy_number or i),
                item.location or "-",
                item.call_number or "-",
                item.barcode or "-",
                item.status,
                item.due_date or "-",
            )
        
        # Select the row matching the selected holding
        if self.selected_holding and self.holdings:
            for i, h in enumerate(self.holdings):
                if h.item_id == self.selected_holding.item_id:
                    table.cursor_coordinate = (i, 0)
                    break
        
        table.focus()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Update item details when a different row is highlighted."""
        if event.cursor_row is not None and 0 <= event.cursor_row < len(self.holdings):
            self.selected_holding = self.holdings[event.cursor_row]
            details_widget = self.query_one("#item-details", Static)
            details_widget.update(self._format_item_details())
    
    def _format_biblio_details(self) -> str:
        """Format bibliographic record for display."""
        if not self.record:
            return "Record information not available."
        
        lines = []
        
        # Title
        title = self.record.title or "Unknown Title"
        lines.append(f"Title:      {title}")
        
        # Author
        if self.record.author:
            lines.append(f"Author:     {self.record.author}")
        
        # Publication info
        pub_parts = []
        if self.record.publisher:
            pub_parts.append(self.record.publisher)
        if self.record.publication_year:
            pub_parts.append(self.record.publication_year)
        if pub_parts:
            lines.append(f"Published:  {', '.join(pub_parts)}")
        
        # ISBN
        if self.record.isbn:
            lines.append(f"ISBN:       {self.record.isbn}")
        
        # Call Number(s) - combined on one line using short label
        call_label = self.config.get_call_number_label_short()
        display_mode = self.config.call_number_display
        
        call_parts = []
        if display_mode == "both":
            if self.record.call_number_lcc:
                call_parts.append(f"LOC: {self.record.call_number_lcc}")
            if self.record.call_number_dewey:
                call_parts.append(f"DDC: {self.record.call_number_dewey}")
            if call_parts:
                lines.append(f"{call_label}:      {' | '.join(call_parts)}")
            elif self.record.call_number:
                lines.append(f"{call_label}:      {self.record.call_number}")
        elif display_mode == "lcc":
            cn = self.record.call_number_lcc or self.record.call_number
            if cn:
                lines.append(f"{call_label}:      {cn}")
        elif display_mode == "dewey":
            cn = self.record.call_number_dewey or self.record.call_number
            if cn:
                lines.append(f"{call_label}:      {cn}")
        
        return "\n".join(lines)
    
    def _format_item_details(self) -> str:
        """Format the selected holding item details."""
        if not self.selected_holding:
            return "Select an item to view details."
        
        item = self.selected_holding
        call_label = self.config.get_call_number_label()
        
        lines = []
        
        # Library and Location
        lines.append(f"Library:   {item.library_name or item.library_id}")
        if item.location:
            lines.append(f"Location:  {item.location}")
        
        # Call Number
        if item.call_number:
            lines.append(f"{call_label}: {item.call_number}")
        
        # Copy Number
        if item.copy_number:
            lines.append(f"Copy:      {item.copy_number}")
        
        # Barcode
        if item.barcode:
            lines.append(f"Barcode:   {item.barcode}")
        
        # Item Type
        if item.item_type:
            lines.append(f"Type:      {item.item_type}")
        
        # Status
        lines.append(f"Status:    {item.status}")
        
        # Due Date (if on loan)
        if item.due_date:
            lines.append(f"Due Date:  {item.due_date}")
        
        # Public Note
        if item.public_note:
            lines.append(f"Note:      {item.public_note}")
        
        return "\n".join(lines)
    
    def action_go_back(self) -> None:
        """Go back to the item detail screen."""
        self.app.pop_screen()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "holding_detail"})
