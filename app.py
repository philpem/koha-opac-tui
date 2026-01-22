#!/usr/bin/env python3
"""
Koha OPAC TUI - A Text-Based User Interface for Koha Library System

A nostalgic terminal-based OPAC interface inspired by classic library
systems like Dynix and BLCMP from the 1990s and early 2000s.

Usage:
    python app.py [--theme THEME] [--server URL]

Options:
    --theme     Color theme: amber, green, white, blue (default: amber)
    --server    Koha server URL (default: from config or demo server)
"""

import argparse
import asyncio
import sys
from typing import Any, Dict, Optional

from textual.app import App

from utils.config import KohaConfig, get_config
from utils.themes import get_theme, get_theme_css, THEMES
from api.client import KohaAPIClient
from api.mock_client import MockKohaAPIClient
from screens import (
    MainMenuScreen,
    SearchScreen,
    SearchResultsScreen,
    ItemDetailScreen,
    HoldingDetailScreen,
    FullBiblioScreen,
    MarcDetailScreen,
    SettingsScreen,
    AboutScreen,
    HelpScreen,
)


class KohaOPACApp(App):
    """
    Main application class for the Koha OPAC TUI.
    
    This application provides a retro terminal-style interface for
    searching and browsing a Koha library catalog.
    """
    
    TITLE = "Koha OPAC Terminal"
    
    CSS = """
    /* Base styles - will be overridden by theme */
    Screen {
        layout: vertical;
    }
    
    #header {
        dock: top;
        height: 2;
        width: 100%;
    }
    
    #main-content {
        height: 1fr;
        padding: 0 2;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        width: 100%;
    }
    
    #welcome-message {
        text-align: center;
        padding: 1 0;
    }
    
    #menu-container {
        margin: 1 2;
    }
    
    #main-menu {
        height: auto;
        max-height: 15;
    }
    
    #search-title {
        text-align: center;
        padding: 1;
    }
    
    #examples-box {
        margin: 1 2;
        height: auto;
    }
    
    #input-area {
        height: auto;
        padding: 0 0;
    }
    
    #search-input {
        width: 100%;
        margin: 0 0 1 0;
    }
    
    #search-info {
        padding: 0 0;
        text-style: italic;
    }
    
    #column-header {
        padding: 0 0;
    }
    
    #results-list {
        height: 16;
        margin: 0 0;
        scrollbar-gutter: stable;
        overflow-y: scroll;
    }
    
    #results-list > ListItem {
        height: 2;
    }
    
    #pagination-info {
        text-align: center;
        padding: 0;
    }
    
    #loading {
        width: 100%;
        height: auto;
    }
    
    LoadingIndicator {
        height: 3;
    }
    
    #biblio-section {
        height: auto;
    }
    
    #biblio-details {
        padding: 0 0;
    }
    
    #detail-container {
        margin: 0 0;
    }
    
    #holdings-section {
        height: auto;
        padding: 0 0;
    }
    
    #holdings-title {
        margin-top: 1;
    }
    
    #holdings-table {
        height: auto;
        max-height: 5;
    }
    
    #holdings-summary {
        padding: 0 0;
    }
    
    #biblio-scroll {
        height: 1fr;
        padding: 0 0;
    }
    
    #holding-scroll {
        height: 1fr;
        padding: 0 0;
    }
    
    Rule {
        margin: 1 0;
    }
    
    /* Settings screen */
    #settings-title {
        text-align: center;
        padding: 1;
    }
    
    #settings-container {
        margin: 1 4;
        height: 1fr;
    }
    
    .section-title {
        text-style: bold underline;
        padding: 1 0;
    }
    
    .setting-row {
        height: auto;
        padding: 0 0 1 0;
    }
    
    .setting-label {
        width: 20;
        padding-right: 1;
    }
    
    #theme-select {
        layout: horizontal;
        height: auto;
    }
    
    #theme-select RadioButton {
        width: auto;
        padding-right: 2;
    }
    
    #theme-row {
        height: auto;
    }
    
    #button-row {
        padding-top: 1;
        height: auto;
    }
    
    #button-row Button {
        margin-right: 1;
    }
    
    #status-message {
        height: auto;
    }
    
    /* About screen */
    #about-text {
        text-align: center;
    }
    
    /* Help screen */
    #help-container {
        padding: 1;
    }
    
    /* Holding detail screen */
    #holding-scroll {
        height: 1fr;
        padding: 0 0;
    }
    
    #library-title {
        text-style: bold;
        padding: 1 0 0 0;
    }
    
    #item-title {
        padding: 1 0 0 0;
    }
    
    #item-details {
        padding: 0 0;
    }
    """
    
    def __init__(self, config: Optional[KohaConfig] = None):
        self.config = config or get_config()
        self._api_client: Optional[KohaAPIClient] = None
        super().__init__()
    
    def get_css_variables(self) -> dict[str, str]:
        """Get CSS variables based on current theme."""
        theme = get_theme(self.config.theme)
        return {
            # Theme colors
            "primary": theme.primary,
            "secondary": theme.secondary,
            "background": theme.background,
            "border": theme.border,
            "header-bg": theme.header_bg,
            "header-fg": theme.header_fg,
            "highlight-bg": theme.highlight_bg,
            "dim": theme.dim,
            # Required Textual variables
            "foreground": theme.primary,
            "surface": theme.background,
            "panel": theme.background,
            "boost": theme.highlight_bg,
            "warning": "#FFB000",
            "error": "#FF6666",
            "success": "#33FF33",
            "accent": theme.secondary,
            "primary-background": theme.background,
            "primary-foreground": theme.primary,
            "secondary-background": theme.highlight_bg,
            "secondary-foreground": theme.secondary,
            "foreground-muted": theme.dim,
            "foreground-disabled": theme.dim,
            "text": theme.primary,
            "text-muted": theme.dim,
            "text-disabled": theme.dim,
            "text-primary": theme.primary,
            "text-secondary": theme.secondary,
            "text-accent": theme.secondary,
            "text-success": "#33FF33",
            "text-warning": "#FFB000",
            "text-error": "#FF6666",
            # Muted color variants
            "success-muted": "#1a331a",
            "warning-muted": "#332200",
            "error-muted": "#331a1a",
            "accent-muted": theme.highlight_bg,
            "primary-muted": theme.highlight_bg,
            "secondary-muted": theme.highlight_bg,
            # Success variants
            "success-darken-1": "#29cc29",
            "success-darken-2": "#1f991f",
            "success-darken-3": "#146614",
            "success-lighten-1": "#5cff5c",
            "success-lighten-2": "#85ff85",
            "success-lighten-3": "#adffad",
            # Warning variants
            "warning-darken-1": "#cc8c00",
            "warning-darken-2": "#996900",
            "warning-darken-3": "#664600",
            "warning-lighten-1": "#ffc033",
            "warning-lighten-2": "#ffd066",
            "warning-lighten-3": "#ffe099",
            # Error variants
            "error-darken-1": "#cc5252",
            "error-darken-2": "#993d3d",
            "error-darken-3": "#662929",
            "error-lighten-1": "#ff8585",
            "error-lighten-2": "#ffa3a3",
            "error-lighten-3": "#ffc2c2",
            # Surface variants (for DataTable zebra stripes etc.)
            "surface-darken-1": theme.highlight_bg,
            "surface-darken-2": theme.highlight_bg,
            "surface-darken-3": theme.highlight_bg,
            "surface-lighten-1": theme.highlight_bg,
            "surface-lighten-2": theme.highlight_bg,
            "surface-lighten-3": theme.highlight_bg,
            # Panel variants (for RadioSet etc.)
            "panel-darken-1": theme.highlight_bg,
            "panel-darken-2": theme.highlight_bg,
            "panel-darken-3": theme.highlight_bg,
            "panel-lighten-1": theme.highlight_bg,
            "panel-lighten-2": theme.highlight_bg,
            "panel-lighten-3": theme.highlight_bg,
            # Accent variants
            "accent-darken-1": theme.highlight_bg,
            "accent-darken-2": theme.highlight_bg,
            "accent-darken-3": theme.highlight_bg,
            "accent-lighten-1": theme.secondary,
            "accent-lighten-2": theme.secondary,
            "accent-lighten-3": theme.secondary,
            # Primary variants
            "primary-darken-1": theme.highlight_bg,
            "primary-darken-2": theme.highlight_bg,
            "primary-darken-3": theme.highlight_bg,
            "primary-lighten-1": theme.secondary,
            "primary-lighten-2": theme.secondary,
            "primary-lighten-3": theme.secondary,
            # Secondary variants
            "secondary-darken-1": theme.highlight_bg,
            "secondary-darken-2": theme.highlight_bg,
            "secondary-darken-3": theme.highlight_bg,
            "secondary-lighten-1": theme.secondary,
            "secondary-lighten-2": theme.secondary,
            "secondary-lighten-3": theme.secondary,
            # Block/hover variables
            "block-cursor-background": theme.highlight_bg,
            "block-cursor-foreground": theme.secondary,
            "block-cursor-text-style": "bold",
            "block-hover-background": theme.highlight_bg,
            "block-cursor-blurred-background": theme.background,
            "block-cursor-blurred-foreground": theme.dim,
            "block-cursor-blurred-text-style": "none",
            # Scrollbar variables
            "scrollbar": theme.dim,
            "scrollbar-hover": theme.primary,
            "scrollbar-active": theme.secondary,
            "scrollbar-background": theme.background,
            "scrollbar-background-hover": theme.highlight_bg,
            "scrollbar-background-active": theme.highlight_bg,
            "scrollbar-corner-color": theme.background,
            "scrollbar-size": "1",
            "scrollbar-size-vertical": "1",
            "scrollbar-size-horizontal": "1",
            # Link colors
            "link-background": theme.background,
            "link-background-hover": theme.highlight_bg,
            "link-color": theme.secondary,
            "link-color-hover": theme.secondary,
            "link-style": "underline",
            "link-style-hover": "bold underline",
            # Footer/header
            "footer-background": theme.header_bg,
            "footer-foreground": theme.header_fg,
            "footer-key-background": theme.background,
            "footer-key-foreground": theme.primary,
            "footer-description-background": theme.header_bg,
            "footer-description-foreground": theme.header_fg,
            # Input
            "input-cursor-background": theme.primary,
            "input-cursor-foreground": theme.background,
            "input-cursor-text-style": "none",
            "input-selection-background": theme.highlight_bg,
            # Border
            "border-blurred": theme.dim,
            # Button
            "button-foreground": theme.primary,
            "button-color-foreground": theme.header_fg,
            "button-focus-text-style": "bold",
            "button-background": theme.highlight_bg,
            "button-background-hover": theme.highlight_bg,
            "button-background-active": theme.background,
        }
    
    @property
    def css(self) -> str:
        """Return combined CSS with theme."""
        theme = get_theme(self.config.theme)
        theme_css = get_theme_css(theme)
        return self.CSS + theme_css
    
    async def on_mount(self) -> None:
        """Initialize the application on mount."""
        # Create API client (mock or real based on config)
        if self.config.demo_mode:
            self._api_client = MockKohaAPIClient(self.config)
        else:
            self._api_client = KohaAPIClient(self.config)
        await self._api_client.__aenter__()
        
        # Show main menu
        await self.push_screen(MainMenuScreen(self.config))
    
    async def on_unmount(self) -> None:
        """Clean up on unmount."""
        if self._api_client:
            await self._api_client.__aexit__(None, None, None)
    
    def push_screen(self, screen_name: str | object, params: Optional[Dict[str, Any]] = None):
        """Push a screen by name or instance."""
        if isinstance(screen_name, str):
            # Create screen instance by name
            screen = self._create_screen(screen_name, params or {})
            if screen:
                return super().push_screen(screen)
        else:
            # It's already a screen instance
            return super().push_screen(screen_name)
    
    def _create_screen(self, name: str, params: Dict[str, Any]) -> Optional[object]:
        """Create a screen instance by name."""
        if name == "main_menu":
            return MainMenuScreen(self.config)
        
        elif name == "search":
            return SearchScreen(
                self.config,
                search_type=params.get("search_type", "title"),
                prompt=params.get("prompt", "Search"),
            )
        
        elif name == "results":
            return SearchResultsScreen(
                self.config,
                self._api_client,
                query=params.get("query", ""),
                search_type=params.get("search_type", "title"),
            )
        
        elif name == "detail":
            return ItemDetailScreen(
                self.config,
                self._api_client,
                biblio_id=params.get("biblio_id", 0),
            )
        
        elif name == "holding_detail":
            return HoldingDetailScreen(
                self.config,
                record=params.get("record"),
                holdings=params.get("holdings", []),
                selected_holding=params.get("selected_holding"),
            )
        
        elif name == "full_biblio":
            return FullBiblioScreen(
                self.config,
                record=params.get("record"),
            )
        
        elif name == "marc_detail":
            return MarcDetailScreen(
                self.config,
                record=params.get("record"),
            )
        
        elif name == "settings":
            return SettingsScreen(self.config)
        
        elif name == "about":
            return AboutScreen(self.config)
        
        elif name == "help":
            return HelpScreen(self.config, context=params.get("context", "general"))
        
        return None
    
    def on_settings_screen_settings_changed(self, event) -> None:
        """Handle settings changes."""
        self.config = event.config
        # Reload the app's CSS to pick up theme changes
        self.refresh_css()


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Koha OPAC TUI - A retro terminal interface for Koha"
    )
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        help="Color theme to use"
    )
    parser.add_argument(
        "--server",
        help="Koha server URL"
    )
    parser.add_argument(
        "--library",
        help="Library name to display"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with mock data (no server required)"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Load configuration
    config = get_config()
    
    # Override with command line arguments
    if args.theme:
        config.theme = args.theme
    if args.server:
        config.base_url = args.server
    if args.library:
        config.library_name = args.library
    
    # Demo mode ONLY from command line flag, never from config
    config.demo_mode = args.demo
    
    # Run the application
    app = KohaOPACApp(config)
    app.run()


if __name__ == "__main__":
    main()
