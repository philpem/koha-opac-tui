"""
Full Bibliographic Details Screen - Displays complete bibliographic information
without the holdings table, allowing full view of all record details.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding

from api.client import BiblioRecord
from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar


class FullBiblioScreen(Screen):
    """
    Full bibliographic details view without holdings.
    Shows all available record information in a scrollable view.
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
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = config
        self.record = record
    
    def compose(self) -> ComposeResult:
        """Compose the full biblio screen layout."""
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Dial Pac",
            id="header"
        )
        
        with Container(id="main-content"):
            yield Static("FULL BIBLIOGRAPHIC DETAILS", id="biblio-title", classes="section-title")
            with ScrollableContainer(id="biblio-scroll"):
                yield Static(self._format_full_details(), id="biblio-details")
        
        yield FooterBar(
            prompt="",
            shortcuts="F1=Help, Esc=Back",
            id="status-bar"
        )
    
    def _format_full_details(self) -> str:
        """Format complete bibliographic record for display."""
        if not self.record:
            return "Record information not available."
        
        record = self.record
        lines = []
        
        # Title
        lines.append(f"Title:       {record.title or 'Unknown Title'}")
        lines.append("")
        
        # Author(s) - may be long with contributors
        if record.author:
            # Split by | to show contributors on separate lines if long
            authors = record.author.split(" | ")
            if len(authors) == 1:
                lines.append(f"Author:      {authors[0]}")
            else:
                lines.append(f"Author:      {authors[0]}")
                for contrib in authors[1:]:
                    lines.append(f"Contributor: {contrib}")
        lines.append("")
        
        # Publication information
        if record.publisher:
            lines.append(f"Publisher:   {record.publisher}")
        if record.publication_year:
            lines.append(f"Year:        {record.publication_year}")
        if record.publisher or record.publication_year:
            lines.append("")
        
        # ISBN
        if record.isbn:
            lines.append(f"ISBN:        {record.isbn}")
            lines.append("")
        
        # Call Numbers
        call_label = self.config.get_call_number_label()
        display_mode = self.config.call_number_display
        
        has_call_number = False
        if display_mode in ["both", "lcc"] and record.call_number_lcc:
            lines.append(f"LOC {call_label}:  {record.call_number_lcc}")
            has_call_number = True
        if display_mode in ["both", "dewey"] and record.call_number_dewey:
            lines.append(f"DDC {call_label}:  {record.call_number_dewey}")
            has_call_number = True
        if not has_call_number and record.call_number:
            lines.append(f"{call_label}:  {record.call_number}")
            has_call_number = True
        if has_call_number:
            lines.append("")
        
        # Edition
        if record.edition:
            lines.append(f"Edition:     {record.edition}")
            lines.append("")
        
        # Physical description
        if record.physical_description:
            lines.append(f"Physical:    {record.physical_description}")
            lines.append("")
        
        # Series
        if record.series:
            lines.append(f"Series:      {record.series}")
            lines.append("")
        
        # Subjects
        if record.subjects:
            lines.append("Subjects:")
            for subject in record.subjects:
                lines.append(f"  • {subject}")
            lines.append("")
        
        # Notes
        if record.notes:
            lines.append(f"Notes:       {record.notes}")
            lines.append("")
        
        # Summary - show full, wrapped
        if record.summary:
            lines.append("Summary:")
            # Word wrap the summary
            words = record.summary.split()
            current_line = "  "
            for word in words:
                if len(current_line) + len(word) + 1 > 76:
                    lines.append(current_line)
                    current_line = "  " + word
                else:
                    if current_line == "  ":
                        current_line += word
                    else:
                        current_line += " " + word
            if current_line.strip():
                lines.append(current_line)
            lines.append("")
        
        # Record ID
        lines.append(f"Record ID:   {record.biblio_id}")
        
        return "\n".join(lines)
    
    def action_go_back(self) -> None:
        """Go back to the item detail screen."""
        self.app.pop_screen()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "full_biblio"})
