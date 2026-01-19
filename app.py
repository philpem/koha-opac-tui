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
from textual.css.stylesheet import Stylesheet

from utils.config import KohaConfig, get_config
from utils.themes import get_theme, get_theme_css, THEMES
from api.client import KohaAPIClient
from screens import (
    MainMenuScreen,
    SearchScreen,
    SearchResultsScreen,
    ItemDetailScreen,
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
        padding: 1;
    }
    
    #status-bar {
        dock: bottom;
        height: 3;
        width: 100%;
    }
    
    #welcome-message {
        text-align: center;
        padding: 1 0;
    }
    
    #menu-container {
        margin: 1 4;
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
        margin: 1 4;
        height: auto;
    }
    
    #input-area {
        height: auto;
        padding: 0 1;
    }
    
    #search-input {
        width: 100%;
        margin: 0 0 1 0;
    }
    
    #search-info {
        padding: 0 1;
        text-style: italic;
    }
    
    #column-header {
        padding: 0 1;
    }
    
    #results-list {
        height: 1fr;
        margin: 0 1;
    }
    
    #pagination-info {
        text-align: center;
        padding: 1;
    }
    
    #loading {
        width: 100%;
        height: auto;
    }
    
    LoadingIndicator {
        height: 3;
    }
    
    #biblio-section {
        height: 1fr;
        max-height: 50%;
    }
    
    #detail-container {
        margin: 0 2;
    }
    
    #holdings-section {
        height: 1fr;
        padding: 0 2;
    }
    
    #holdings-table {
        height: 1fr;
        max-height: 10;
    }
    
    #holdings-summary {
        padding: 1;
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
    
    #button-row {
        padding-top: 2;
        height: auto;
    }
    
    #button-row Button {
        margin-right: 1;
    }
    
    #status-message {
        padding: 1;
        text-style: italic;
    }
    
    /* About screen */
    #about-text {
        text-align: center;
    }
    
    /* Help screen */
    #help-container {
        padding: 1;
    }
    """
    
    def __init__(self, config: Optional[KohaConfig] = None):
        super().__init__()
        self.config = config or get_config()
        self._api_client: Optional[KohaAPIClient] = None
        self._apply_theme()
    
    def _apply_theme(self) -> None:
        """Apply the current theme CSS."""
        theme = get_theme(self.config.theme)
        theme_css = get_theme_css(theme)
        # Combine base CSS with theme CSS
        self.stylesheet = Stylesheet()
        self.stylesheet.parse(self.CSS + theme_css)
    
    async def on_mount(self) -> None:
        """Initialize the application on mount."""
        # Create API client
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
        
        elif name == "settings":
            return SettingsScreen(self.config)
        
        elif name == "about":
            return AboutScreen()
        
        elif name == "help":
            return HelpScreen()
        
        return None
    
    def on_settings_screen_settings_changed(self, event) -> None:
        """Handle settings changes."""
        self.config = event.config
        self._apply_theme()
        # Force refresh
        self.refresh(layout=True)


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
    
    # Run the application
    app = KohaOPACApp(config)
    app.run()


if __name__ == "__main__":
    main()
