"""
Settings Screen - Configure user display preferences.
"""

from typing import Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Static, Button, RadioButton, RadioSet
from textual.binding import Binding
from textual.message import Message

from utils.config import KohaConfig
from utils.themes import THEMES
from widgets import HeaderBar, FooterBar


class SettingsScreen(Screen):
    """
    Settings configuration screen.
    Allows users to configure display preferences.
    Library-specific settings are configured via config file or command line.
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
            yield Static("DISPLAY PREFERENCES", classes="settings-header")
            yield Static("")
            
            yield Static("Color Theme:")
            with Horizontal(id="theme-row"):
                with RadioSet(id="theme-select"):
                    for theme_id, theme in THEMES.items():
                        is_selected = theme_id == self.config.theme
                        yield RadioButton(
                            theme.name,
                            value=is_selected,
                            id=f"theme-{theme_id}"
                        )
            
            yield Static("")
            yield Static("Search Results Spacing:")
            with Horizontal(id="spacing-row"):
                with RadioSet(id="spacing-select"):
                    yield RadioButton(
                        "Compact",
                        value=not self.config.result_spacing,
                        id="spacing-compact"
                    )
                    yield RadioButton(
                        "Spaced (blank line between)",
                        value=self.config.result_spacing,
                        id="spacing-spaced"
                    )
            
            yield Static("")
            with Horizontal(id="button-row"):
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn")
            
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
    
    def _save_settings(self) -> None:
        """Save the current settings."""
        status = self.query_one("#status-message", Static)
        
        try:
            # Get selected theme
            theme = self.config.theme  # Default to current
            theme_set = self.query_one("#theme-select", RadioSet)
            if theme_set.pressed_button:
                theme_id = theme_set.pressed_button.id
                if theme_id and theme_id.startswith("theme-"):
                    theme = theme_id.replace("theme-", "")
            
            # Get selected spacing option
            result_spacing = self.config.result_spacing  # Default to current
            spacing_set = self.query_one("#spacing-select", RadioSet)
            if spacing_set.pressed_button:
                btn_id = spacing_set.pressed_button.id
                result_spacing = (btn_id == "spacing-spaced")
            
            # Update config
            self.config.theme = theme
            self.config.result_spacing = result_spacing
            
            # Save to file
            self.config.save()
            
            status.update("Settings saved!")
            
            # Notify app to reload theme
            self.app.post_message(self.SettingsChanged(self.config))
            
        except Exception as e:
            status.update(f"Error: {e}")
    
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
