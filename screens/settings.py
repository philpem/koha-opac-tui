"""
Settings Screen - Configure application settings including theme and Koha connection.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.screen import Screen
from textual.widgets import Static, Input, Button, Select, Label, RadioButton, RadioSet
from textual.binding import Binding

from utils.config import KohaConfig
from utils.themes import THEMES, get_theme


class SettingsScreen(Screen):
    """
    Settings configuration screen.
    Allows users to configure connection settings and display preferences.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("ctrl+s", "save_settings", "Save"),
    ]
    
    def __init__(self, config: KohaConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
    
    def compose(self) -> ComposeResult:
        """Compose the settings screen layout."""
        yield Static("── SETTINGS ──", id="settings-title", classes="box-title")
        
        with Container(id="settings-container"):
            with Container(classes="content-box"):
                # Connection Settings
                yield Static("Connection Settings", classes="section-title")
                
                with Horizontal(classes="setting-row"):
                    yield Label("Koha Server URL:", classes="setting-label")
                    yield Input(
                        value=self.config.base_url,
                        id="server-url",
                        placeholder="https://your-koha-server.org"
                    )
                
                with Horizontal(classes="setting-row"):
                    yield Label("Library Name:", classes="setting-label")
                    yield Input(
                        value=self.config.library_name,
                        id="library-name",
                        placeholder="Your Library Name"
                    )
                
                yield Static("")  # Spacer
                
                # Display Settings
                yield Static("Display Settings", classes="section-title")
                
                with Horizontal(classes="setting-row"):
                    yield Label("Color Theme:", classes="setting-label")
                    with RadioSet(id="theme-select"):
                        for theme_id, theme in THEMES.items():
                            is_selected = theme_id == self.config.theme
                            yield RadioButton(
                                theme.name,
                                value=is_selected,
                                id=f"theme-{theme_id}"
                            )
                
                with Horizontal(classes="setting-row"):
                    yield Label("Items per page:", classes="setting-label")
                    yield Input(
                        value=str(self.config.items_per_page),
                        id="items-per-page",
                        placeholder="10"
                    )
                
                yield Static("")  # Spacer
                
                # Buttons
                with Horizontal(id="button-row"):
                    yield Button("Save Settings", id="save-btn", variant="primary")
                    yield Button("Cancel", id="cancel-btn")
                    yield Button("Test Connection", id="test-btn")
        
        # Status message
        yield Static("", id="status-message")
        
        # Status bar
        yield Static(
            "Enter settings and press Save, or Escape to cancel.",
            id="status-bar",
            classes="status-bar"
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
            items_per_page_str = self.query_one("#items-per-page", Input).value.strip()
            
            # Validate
            if not server_url:
                status.update("Error: Server URL is required")
                return
            
            try:
                items_per_page = int(items_per_page_str)
                if items_per_page < 1:
                    raise ValueError()
            except ValueError:
                status.update("Error: Items per page must be a positive number")
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
            self.config.items_per_page = items_per_page
            self.config.theme = theme
            
            # Save to file
            self.config.save()
            
            status.update("Settings saved successfully!")
            
            # Notify app to reload theme
            self.app.post_message(self.SettingsChanged(self.config))
            
        except Exception as e:
            status.update(f"Error saving settings: {e}")
    
    def _test_connection(self) -> None:
        """Test the connection to the Koha server."""
        status = self.query_one("#status-message", Static)
        status.update("Testing connection...")
        
        self.run_worker(self._do_test_connection())
    
    async def _do_test_connection(self) -> None:
        """Actually test the connection."""
        import httpx
        
        server_url = self.query_one("#server-url", Input).value.strip()
        if not server_url:
            self.call_from_thread(self._update_status, "Error: Enter a server URL first")
            return
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Try to access the public API
                url = f"{server_url.rstrip('/')}/api/v1/public/libraries"
                response = await client.get(url)
                
                if response.status_code == 200:
                    self.call_from_thread(
                        self._update_status,
                        "✓ Connection successful!"
                    )
                elif response.status_code == 404:
                    self.call_from_thread(
                        self._update_status,
                        "✓ Server found, but API may not be enabled"
                    )
                else:
                    self.call_from_thread(
                        self._update_status,
                        f"⚠ Server responded with status {response.status_code}"
                    )
        except httpx.ConnectError:
            self.call_from_thread(
                self._update_status,
                "✗ Could not connect to server"
            )
        except httpx.TimeoutException:
            self.call_from_thread(
                self._update_status,
                "✗ Connection timed out"
            )
        except Exception as e:
            self.call_from_thread(
                self._update_status,
                f"✗ Error: {e}"
            )
    
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
    
    class SettingsChanged:
        """Message indicating settings have changed."""
        def __init__(self, config: KohaConfig):
            self.config = config
