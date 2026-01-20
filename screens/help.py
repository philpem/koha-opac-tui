"""
Help Screen - Displays context-sensitive help for each screen.
"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding

from utils.help_text import get_help_for_screen, get_help_title
from widgets import HeaderBar, FooterBar


class HelpScreen(Screen):
    """
    Help screen showing context-sensitive usage instructions.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("q", "go_back", "Back", show=False),
    ]
    
    def __init__(self, config=None, context: str = "general", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.context = context
    
    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        # Use config if available, otherwise defaults
        library_name = self.config.library_name if self.config else "PUBLIC LIBRARY"
        help_title = get_help_title(self.context)
        
        yield HeaderBar(
            library_name=library_name,
            opac_name=help_title,
            id="header"
        )
        
        with ScrollableContainer(id="help-container"):
            yield Static(get_help_for_screen(self.context), id="help-text")
        
        yield FooterBar(
            prompt="",
            shortcuts="Esc=Return to previous screen",
            id="status-bar"
        )
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
