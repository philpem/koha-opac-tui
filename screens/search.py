"""
Search Screen - Interface for entering search queries.
Inspired by the classic Dynix author/title search screens.
"""

from typing import Dict, Any, Optional
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Static, Input
from textual.binding import Binding

from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar


class SearchScreen(Screen):
    """
    Search input screen.
    Allows users to enter search terms for various search types.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+c", "go_back", "Back", show=False),
        Binding("f1", "show_help", "Help"),
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
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Dial Pac",
            id="header"
        )
        
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
        with Container(id="input-area"):
            yield Static(self._get_prompt_text(), id="prompt-label")
            yield Input(
                placeholder=f"Enter {self.prompt.lower()}...",
                id="search-input",
                classes="input-field"
            )
        
        # Footer with shortcuts
        yield FooterBar(
            prompt="",
            shortcuts="Enter=Search, F1=Help, Esc=Back",
            id="status-bar"
        )
    
    def _get_examples_text(self) -> str:
        """Get example text based on search type."""
        examples = {
            "title": (
                "Examples:\n\n"
                "    CATS                (Single keyword)\n"
                "    PLAYER OF GAMES     (Multiple keywords)\n"
                "    FOUNDATION          (Partial title)\n\n"
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
                "    STEPHEN KING       (Author's full name)\n"
                "    HEMINGW            (Note: OK to shorten name)\n"
                "    BANKS, IAIN M      (Last name, First name)"
            ),
            "subject": (
                "Examples:\n\n"
                "    HISTORY            (Single subject)\n"
                "    WORLD WAR          (Subject phrase)\n"
                "    COOKING FRENCH     (Multiple terms)"
            ),
            "series": (
                "Examples:\n\n"
                "    FOUNDATION         (Series name)\n"
                "    DISCWORLD          (Series name)\n"
                "    SHERLOCK           (Partial series name)"
            ),
            "keyword": (
                "SUPER SEARCH - Search all fields\n\n"
                "Examples:\n\n"
                "    PYTHON PROGRAMMING     (Any keywords)\n"
                "    SHAKESPEARE TRAGEDY    (Author + Subject)\n"
                "    1969 MOON              (Year + Topic)"
            ),
            "isbn": (
                # Pride and Prejudice, 2002 Penguin Classics edition
                "Examples:\n\n"
                "    9780141439518          (ISBN-13)\n"
                "    0141439513             (ISBN-10)\n"
                "    978-0-14-143951-8      (With dashes OK)"
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
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "search"})
