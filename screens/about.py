"""
About Screen - Information about the application.
"""

from textual.app import ComposeResult
from textual.containers import Container, Center
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding


ABOUT_TEXT = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                         KOHA OPAC TEXT TERMINAL                              ║
║                              Version 1.0.0                                   ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  A nostalgic text-based interface for the Koha Integrated Library System,   ║
║  inspired by the classic Dynix and BLCMP library terminals of the 1990s.    ║
║                                                                              ║
║  This application connects to any Koha ILS via its REST API to provide:     ║
║                                                                              ║
║    • Catalog searching by title, author, subject, ISBN, and more            ║
║    • Detailed bibliographic record viewing                                   ║
║    • Real-time item availability and holdings information                    ║
║    • Classic terminal aesthetics with customizable color themes              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Built with:                                                                 ║
║    • Textual - Modern TUI framework for Python                              ║
║    • Koha REST API - Open source ILS                                        ║
║                                                                              ║
║  For more information about Koha:                                            ║
║    https://koha-community.org                                                ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Color Themes Available:                                                     ║
║    • Amber  - Classic amber phosphor terminal look                          ║
║    • Green  - Green phosphor terminal (P1 phosphor)                         ║
║    • White  - Monochrome white on black                                     ║
║    • Blue   - Cool blue terminal style                                      ║
║                                                                              ║
║  Change themes in Settings (option 8 from main menu)                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

                    Press any key to return to the main menu
"""


class AboutScreen(Screen):
    """
    About screen showing application information.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("enter", "go_back", "Back", show=False),
        Binding("space", "go_back", "Back", show=False),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the about screen."""
        with Center():
            yield Static(ABOUT_TEXT, id="about-text")
    
    def on_key(self, event) -> None:
        """Any key press returns to main menu."""
        self.app.pop_screen()
    
    def action_go_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
