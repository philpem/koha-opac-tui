"""
About Screen - Information about the application.
"""

from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding

from widgets import HeaderBar, FooterBar


ABOUT_TEXT = """
                     KOHA OPAC TEXT TERMINAL
                          Version 1.0.0

 A nostalgic text-based interface for the Koha Integrated
 Library System, inspired by the classic Dynix and BLCMP
 library terminals of the 1990s.

 This application connects to any Koha ILS via its REST
 API to provide:

   * Catalog searching by title, author, subject, ISBN
   * Detailed bibliographic record viewing
   * Real-time item availability and holdings
   * Classic terminal aesthetics with color themes

 Built with:
   * Textual - Modern TUI framework for Python
   * Koha REST API - Open source ILS

 For more information about Koha:
   https://koha-community.org

 Color Themes Available:
   * Amber  - Classic amber phosphor terminal
   * Green  - Green phosphor (VT100 style)
   * White  - Monochrome white on black
   * Blue   - Cool blue terminal

 Change themes in Settings (option 8 from main menu)
"""


class AboutScreen(Screen):
    """
    About screen showing application information.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("enter", "go_back", "Back", show=False),
        Binding("space", "go_back", "Back", show=False),
        Binding("q", "go_back", "Back", show=False),
    ]
    
    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
    
    def compose(self) -> ComposeResult:
        """Compose the about screen."""
        library_name = self.config.library_name if self.config else "PUBLIC LIBRARY"
        
        yield HeaderBar(
            library_name=library_name,
            opac_name="About",
            id="header"
        )
        
        with ScrollableContainer(id="about-container"):
            yield Static(ABOUT_TEXT, id="about-text")
        
        yield FooterBar(
            prompt="",
            shortcuts="Esc=Return to main menu",
            id="status-bar"
        )
    
    def action_go_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
