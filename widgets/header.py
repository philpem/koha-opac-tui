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
        self.add_class("header-bar")
    
    def on_mount(self) -> None:
        """Start the timer to update time."""
        self.current_time = datetime.now().strftime("%I:%M%p").lower()
        self.set_interval(1, self._update_time)
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
        
        # Build the two-line header
        # Line 1: Date left, Library name center, Time right
        # Line 2: OPAC name centered
        
        width = 80  # Standard terminal width
        
        # Line 1
        left = date_str
        center = self.library_name
        right = self.current_time
        
        # Calculate padding for center alignment
        total_content = len(left) + len(center) + len(right)
        remaining = width - total_content
        left_pad = remaining // 2
        right_pad = remaining - left_pad
        
        line1 = f"{left}{' ' * left_pad}{center}{' ' * right_pad}{right}"
        
        # Line 2: OPAC name centered
        line2 = self.opac_name.center(width)
        
        self.update(f"{line1}\n{line2}")


class FooterBar(Static):
    """
    Footer/status bar widget that displays context-sensitive help.
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
        self.add_class("status-bar")
    
    def on_mount(self) -> None:
        """Set initial content."""
        self._refresh_display()
    
    def _refresh_display(self) -> None:
        """Refresh the footer display."""
        lines = []
        if self.prompt:
            lines.append(self.prompt)
        if self.shortcuts:
            lines.append(self.shortcuts)
        self.update("\n".join(lines) if lines else "")
    
    def set_prompt(self, prompt: str) -> None:
        """Update the prompt text."""
        self.prompt = prompt
        self._refresh_display()
    
    def set_shortcuts(self, shortcuts: str) -> None:
        """Update the shortcuts text."""
        self.shortcuts = shortcuts
        self._refresh_display()
