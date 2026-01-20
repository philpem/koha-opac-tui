"""
Theme definitions for the Koha OPAC TUI.
Provides retro terminal color schemes reminiscent of 1990s library terminals.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class TerminalTheme:
    """Represents a terminal color theme."""
    name: str
    primary: str      # Main text color
    secondary: str    # Highlighted/selected text
    background: str   # Background color
    border: str       # Border/box drawing color
    header_bg: str    # Header background
    header_fg: str    # Header foreground
    highlight_bg: str # Selected item background
    dim: str          # Dimmed/inactive text


# Classic terminal themes
THEMES: Dict[str, TerminalTheme] = {
    "amber": TerminalTheme(
        name="Amber",
        primary="#FFB000",
        secondary="#FFCC00",
        background="#1A1200",
        border="#FFB000",
        header_bg="#FFB000",
        header_fg="#1A1200",
        highlight_bg="#332200",
        dim="#805800",
    ),
    "green": TerminalTheme(
        name="Green",
        primary="#33FF33",
        secondary="#66FF66",
        background="#001A00",
        border="#33FF33",
        header_bg="#33FF33",
        header_fg="#001A00",
        highlight_bg="#003300",
        dim="#196619",
    ),
    "white": TerminalTheme(
        name="White",
        primary="#CCCCCC",
        secondary="#FFFFFF",
        background="#000000",
        border="#CCCCCC",
        header_bg="#CCCCCC",
        header_fg="#000000",
        highlight_bg="#333333",
        dim="#666666",
    ),
    "blue": TerminalTheme(
        name="Blue",
        primary="#00AAFF",
        secondary="#66CCFF",
        background="#000814",
        border="#00AAFF",
        header_bg="#00AAFF",
        header_fg="#000814",
        highlight_bg="#001428",
        dim="#005580",
    ),
}


def get_theme(name: str) -> TerminalTheme:
    """Get a theme by name, defaulting to amber if not found."""
    return THEMES.get(name.lower(), THEMES["amber"])


def get_theme_css(theme: TerminalTheme) -> str:
    """Generate CSS for the given theme."""
    return f"""
    Screen {{
        background: {theme.background};
    }}
    
    .header-bar {{
        background: {theme.header_bg};
        color: {theme.header_fg};
        text-style: bold;
        padding: 0 1;
        height: 2;
    }}
    
    .content-box {{
        border: solid {theme.border};
        background: {theme.background};
        padding: 1;
    }}
    
    .menu-item {{
        color: {theme.primary};
        padding: 0 2;
    }}
    
    .menu-item:hover {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
    }}
    
    .menu-item:focus {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
    }}
    
    .menu-number {{
        color: {theme.secondary};
        text-style: bold;
    }}
    
    .input-field {{
        border: solid {theme.border};
        background: {theme.background};
        color: {theme.primary};
        padding: 0 1;
    }}
    
    .input-field:focus {{
        border: solid {theme.secondary};
    }}
    
    .status-bar {{
        background: {theme.header_bg};
        color: {theme.header_fg};
        height: 2;
        padding: 0 1;
    }}
    
    .result-item {{
        color: {theme.primary};
        padding: 0 1;
    }}
    
    .result-item:hover {{
        background: {theme.highlight_bg};
    }}
    
    .result-item:focus {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
    }}
    
    .result-item-text {{
        color: {theme.primary};
    }}
    
    .result-number {{
        color: {theme.secondary};
        text-style: bold;
        width: 4;
    }}
    
    .result-title {{
        color: {theme.primary};
    }}
    
    .result-author {{
        color: {theme.dim};
    }}
    
    .result-date {{
        color: {theme.dim};
        width: 12;
        text-align: right;
    }}
    
    .detail-label {{
        color: {theme.dim};
        width: 20;
    }}
    
    .detail-value {{
        color: {theme.primary};
    }}
    
    .holdings-header {{
        background: {theme.header_bg};
        color: {theme.header_fg};
        text-style: bold;
    }}
    
    .holdings-row {{
        color: {theme.primary};
    }}
    
    .holdings-row:hover {{
        background: {theme.highlight_bg};
    }}
    
    .available {{
        color: #00FF00;
        text-style: bold;
    }}
    
    .unavailable {{
        color: #FF6666;
    }}
    
    .prompt-text {{
        color: {theme.primary};
    }}
    
    .help-text {{
        color: {theme.dim};
    }}
    
    Label {{
        color: {theme.primary};
    }}
    
    Static {{
        color: {theme.primary};
    }}
    
    Button {{
        background: {theme.background};
        color: {theme.primary};
        border: solid {theme.border};
    }}
    
    Button:hover {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
    }}
    
    Button:focus {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
        border: solid {theme.secondary};
    }}
    
    DataTable {{
        background: {theme.background};
    }}
    
    DataTable > .datatable--header {{
        background: {theme.header_bg};
        color: {theme.header_fg};
        text-style: bold;
    }}
    
    DataTable > .datatable--cursor {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
    }}
    
    DataTable > .datatable--hover {{
        background: {theme.highlight_bg};
    }}
    
    Input {{
        background: {theme.background};
        color: {theme.primary};
        border: solid {theme.border};
    }}
    
    Input:focus {{
        border: solid {theme.secondary};
    }}
    
    Input > .input--placeholder {{
        color: {theme.dim};
    }}
    
    ListItem {{
        color: {theme.primary};
        background: {theme.background};
    }}
    
    ListItem:hover {{
        background: {theme.highlight_bg};
    }}
    
    ListView:focus > ListItem.--highlight {{
        background: {theme.highlight_bg};
        color: {theme.secondary};
    }}
    
    #title-display {{
        text-style: bold;
        color: {theme.secondary};
    }}
    
    .box-title {{
        color: {theme.secondary};
        text-style: bold;
    }}
    
    .pagination-info {{
        color: {theme.dim};
        text-align: center;
    }}
    """
