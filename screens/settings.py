"""
Settings Screen - Configure application settings including theme and Koha connection.
"""

from typing import Optional
from textual import work
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, Input, Button, Label, RadioButton, RadioSet
from textual.binding import Binding
from textual.message import Message

from utils.config import KohaConfig
from utils.themes import THEMES
from widgets import HeaderBar, FooterBar


class SettingsScreen(Screen):
    """
    Settings configuration screen.
    Allows users to configure connection settings and display preferences.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save_settings", "Save"),
        Binding("f1", "show_help", "Help"),
    ]
    
    def __init__(self, config: KohaConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
    
    def compose(self) -> ComposeResult:
        """Compose the settings screen layout."""
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Settings",
            id="header"
        )
        
        with Container(id="main-content"):
            yield Static("Server URL:")
            yield Input(
                value=self.config.base_url,
                id="server-url",
                placeholder="https://your-koha-server.org"
            )
            
            yield Static("Library Name:")
            yield Input(
                value=self.config.library_name,
                id="library-name",
                placeholder="Your Library Name"
            )
            
            yield Static("Theme:")
            with Horizontal(id="theme-row"):
                with RadioSet(id="theme-select"):
                    for theme_id, theme in THEMES.items():
                        is_selected = theme_id == self.config.theme
                        yield RadioButton(
                            theme.name,
                            value=is_selected,
                            id=f"theme-{theme_id}"
                        )
            
            with Horizontal(id="button-row"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn")
                yield Button("Test", id="test-btn")
            
            yield Static("", id="status-message")
        
        yield FooterBar(
            shortcuts="Ctrl+S=Save, F1=Help, Esc=Cancel",
            id="status-bar"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-btn":
            self._save_settings()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
        elif event.button.id == "test-btn":
            self._test_connection()
    
    def _save_settings(self) -> None:
        """Save the current settings."""
        status = self.query_one("#status-message", Static)
        
        try:
            # Get values from inputs
            server_url = self.query_one("#server-url", Input).value.strip()
            library_name = self.query_one("#library-name", Input).value.strip()
            
            # Validate
            if not server_url:
                status.update("Error: Server URL is required")
                return
            
            # Get selected theme
            theme = self.config.theme  # Default to current
            theme_set = self.query_one("#theme-select", RadioSet)
            if theme_set.pressed_button:
                theme_id = theme_set.pressed_button.id
                if theme_id and theme_id.startswith("theme-"):
                    theme = theme_id.replace("theme-", "")
            
            # Update config
            self.config.base_url = server_url
            self.config.library_name = library_name or "PUBLIC LIBRARY"
            self.config.theme = theme
            
            # Save to file
            self.config.save()
            
            status.update("Settings saved!")
            
            # Notify app to reload theme
            self.app.post_message(self.SettingsChanged(self.config))
            
        except Exception as e:
            status.update(f"Error: {e}")
    
    def _test_connection(self) -> None:
        """Test the connection to the Koha server."""
        status = self.query_one("#status-message", Static)
        status.update("Testing...")
        self._do_test_connection()
    
    @work(exclusive=True)
    async def _do_test_connection(self) -> None:
        """Actually test the connection."""
        import httpx
        
        server_url = self.query_one("#server-url", Input).value.strip()
        if not server_url:
            self._update_status("Error: Enter a server URL first")
            return
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Try to access the public API
                url = f"{server_url.rstrip('/')}/api/v1/public/libraries"
                response = await client.get(url)
                
                if response.status_code == 200:
                    self._update_status("Connection OK!")
                elif response.status_code == 404:
                    self._update_status("Server found, API may not be enabled")
                else:
                    self._update_status(f"Server responded: {response.status_code}")
        except httpx.ConnectError:
            self._update_status("Could not connect to server")
        except httpx.TimeoutException:
            self._update_status("Connection timed out")
        except Exception as e:
            self._update_status(f"Error: {e}")
    
    def _update_status(self, message: str) -> None:
        """Update the status message."""
        status = self.query_one("#status-message", Static)
        status.update(message)
    
    def action_go_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    def action_save_settings(self) -> None:
        """Save settings via keyboard shortcut."""
        self._save_settings()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "settings"})
    
    class SettingsChanged(Message):
        """Message indicating settings have changed."""
        def __init__(self, config: KohaConfig):
            self.config = config
            super().__init__()
