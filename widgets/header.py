"""
Shared widgets for the Koha OPAC TUI.
"""

from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static
from textual.reactive import reactive


class HeaderBar(Static):
    """
    Header bar widget that displays date, library name, and time.
    The time updates automatically.
    """
    
    DEFAULT_CSS = """
    HeaderBar {
        height: 2;
        width: 100%;
        dock: top;
        background: $header-bg;
        color: $header-fg;
        text-style: bold;
    }
    """
    
    current_time = reactive("")
    
    def __init__(
        self,
        library_name: str = "PUBLIC LIBRARY",
        opac_name: str = "Dial Pac",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.library_name = library_name.upper()
        self.opac_name = opac_name
    
    def on_mount(self) -> None:
        """Start the timer to update time."""
        self.current_time = datetime.now().strftime("%I:%M%p").lower()
        self.set_interval(1, self._update_time)
        self._refresh_display()
    
    def on_resize(self, event) -> None:
        """Re-render when resized."""
        self._refresh_display()
    
    def _update_time(self) -> None:
        """Update the current time."""
        self.current_time = datetime.now().strftime("%I:%M%p").lower()
    
    def watch_current_time(self, time: str) -> None:
        """React to time changes."""
        self._refresh_display()
    
    def _refresh_display(self) -> None:
        """Refresh the header display."""
        now = datetime.now()
        date_str = now.strftime("%d %b %Y").upper()
        
        # Get actual width from the widget
        width = self.size.width if self.size.width > 0 else 80
        
        # Line 1: Date left, Library name center, Time right
        left = date_str
        center = self.library_name
        right = self.current_time
        
        # Calculate spacing to center the library name
        # Total: left + space + center + space + right = width
        total_fixed = len(left) + len(center) + len(right)
        total_space = width - total_fixed
        
        if total_space >= 2:
            left_space = (width - len(center)) // 2 - len(left)
            right_space = width - len(left) - left_space - len(center) - len(right)
            line1 = f"{left}{' ' * max(1, left_space)}{center}{' ' * max(1, right_space)}{right}"
        else:
            # Narrow screen - just show what fits
            line1 = f"{left} {center} {right}"
        
        # Line 2: OPAC name centered
        line2 = self.opac_name.center(width)
        
        self.update(f"{line1}\n{line2}")


class FooterBar(Static):
    """
    Footer/status bar widget that displays context-sensitive help.
    """
    
    DEFAULT_CSS = """
    FooterBar {
        height: 1;
        width: 100%;
        dock: bottom;
        background: $header-bg;
        color: $header-fg;
        text-style: bold;
        padding: 0 1;
    }
    """
    
    def __init__(
        self,
        prompt: str = "",
        shortcuts: str = "",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.prompt = prompt
        self.shortcuts = shortcuts
    
    def on_mount(self) -> None:
        """Set initial content."""
        self.update(self.shortcuts)
    
    def set_shortcuts(self, shortcuts: str) -> None:
        """Update the shortcuts text."""
        self.shortcuts = shortcuts
        self.update(self.shortcuts)
