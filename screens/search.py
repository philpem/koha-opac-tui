"""
Search Screen - Interface for entering search queries.
Inspired by the classic Dynix author/title search screens.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Static, Input, Label
from textual.binding import Binding

from utils.config import KohaConfig


class SearchScreen(Screen):
    """
    Search input screen.
    Allows users to enter search terms for various search types.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+c", "go_back", "Back", show=False),
    ]
    
    def __init__(
        self,
        config: KohaConfig,
        search_type: str = "title",
        prompt: str = "Search",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = config
        self.search_type = search_type
        self.prompt = prompt
    
    def compose(self) -> ComposeResult:
        """Compose the search screen layout."""
        # Header bar
        yield Static(self._get_header_text(), id="header", classes="header-bar")
        
        with Container(id="main-content"):
            # Search type title
            yield Static(
                f"── {self.prompt.upper()} SEARCH ──",
                id="search-title",
                classes="box-title"
            )
            
            # Examples box
            with Container(id="examples-box", classes="content-box"):
                yield Static(self._get_examples_text(), id="examples")
            
            # Spacer
            yield Static("", id="spacer")
        
        # Input area at bottom
        with Container(id="input-area", classes="status-bar"):
            yield Static(self._get_prompt_text(), id="prompt-label")
            yield Input(
                placeholder=f"Enter {self.prompt.lower()}...",
                id="search-input",
                classes="input-field"
            )
            yield Static(
                "SO=Start Over, B=Back, ?=Help",
                id="help-hint",
                classes="help-text"
            )
    
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
    
    def _get_examples_text(self) -> str:
        """Get example text based on search type."""
        examples = {
            "title": (
                "Examples:\n\n"
                "    CATS                (Single keyword)\n"
                "    GREAT GATSBY        (Multiple keywords)\n"
                "    HARRY POTTER        (Partial title)\n\n"
                "    (Note: OK to use partial words)"
            ),
            "title_exact": (
                "Examples:\n\n"
                "    THE GREAT GATSBY           (Complete title)\n"
                "    TO KILL A MOCKINGBIRD      (Full exact title)\n\n"
                "    (Note: Enter the complete title)"
            ),
            "author": (
                "Examples:\n\n"
                "    ASIMOV, ISAAC      (Author's full name)\n"
                "    HEMINGW            (Note: OK to shorten name)\n"
                "    KING, STEPHEN      (Last name, First name)"
            ),
            "subject": (
                "Examples:\n\n"
                "    HISTORY            (Single subject)\n"
                "    WORLD WAR          (Subject phrase)\n"
                "    COOKING FRENCH     (Multiple terms)"
            ),
            "series": (
                "Examples:\n\n"
                "    HARRY POTTER       (Series name)\n"
                "    DISCWORLD          (Partial series name)\n"
                "    WHEEL OF TIME      (Full series name)"
            ),
            "keyword": (
                "SUPER SEARCH - Search all fields\n\n"
                "Examples:\n\n"
                "    PYTHON PROGRAMMING     (Any keywords)\n"
                "    SHAKESPEARE TRAGEDY    (Author + Subject)\n"
                "    2020 COVID             (Year + Topic)"
            ),
            "isbn": (
                "Examples:\n\n"
                "    9780134685991          (ISBN-13)\n"
                "    0134685997             (ISBN-10)\n"
                "    978-0-13-468599-1      (With dashes OK)"
            ),
        }
        return examples.get(self.search_type, "Enter your search terms below.")
    
    def _get_prompt_text(self) -> str:
        """Get the input prompt text."""
        if self.search_type == "author":
            return f"Enter the author's name (last, first) :"
        elif self.search_type == "title_exact":
            return f"Enter the exact title :"
        elif self.search_type == "isbn":
            return f"Enter the ISBN :"
        else:
            return f"Enter {self.prompt.lower()} :"
    
    def on_mount(self) -> None:
        """Focus the input on mount."""
        input_widget = self.query_one("#search-input", Input)
        input_widget.focus()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle search submission."""
        query = event.value.strip()
        if query:
            # Navigate to results screen
            self.app.push_screen(
                "results",
                {
                    "query": query,
                    "search_type": self.search_type,
                }
            )
        elif query.upper() == "SO":
            # Start over - go back to main menu
            self.app.pop_screen()
            self.app.pop_screen()  # Pop back to main menu
        elif query.upper() == "B":
            self.action_go_back()
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
