"""
Main Menu Screen - The primary navigation interface for the OPAC.
Inspired by the classic Dynix/BLCMP terminal interface.
"""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Static, ListItem, ListView
from textual.binding import Binding

from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar


class MenuItem(ListItem):
    """A selectable menu item."""
    
    def __init__(self, number: int, label: str, action: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = number
        self.label = label
        self.action = action
    
    def compose(self) -> ComposeResult:
        yield Static(f"  {self.number:2d}. {self.label}")


class MainMenuScreen(Screen):
    """
    The main menu screen of the OPAC.
    Displays options for searching the catalog.
    """
    
    BINDINGS = [
        Binding("1", "select_1", "Title Keywords", show=False),
        Binding("2", "select_2", "Exact Title", show=False),
        Binding("3", "select_3", "Author Browse", show=False),
        Binding("4", "select_4", "Subject Keywords", show=False),
        Binding("5", "select_5", "Series", show=False),
        Binding("6", "select_6", "Super Search", show=False),
        Binding("7", "select_7", "ISBN Search", show=False),
        Binding("8", "select_8", "Settings", show=False),
        Binding("9", "select_9", "About", show=False),
        Binding("0", "select_0", "Quit", show=False),
        Binding("q", "quit_app", "Quit"),
        Binding("escape", "quit_app", "Quit"),
        Binding("question_mark", "show_help", "Help", key_display="?"),
    ]
    
    def __init__(self, config: KohaConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
    
    def compose(self) -> ComposeResult:
        """Compose the main menu layout."""
        # Header bar
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="Dial Pac",
            id="header"
        )
        
        with Container(id="main-content"):
            # Welcome message
            yield Static(
                "Welcome to the Online Public Access Catalog!\n"
                "Please select one of the options below.",
                id="welcome-message"
            )
            
            # Menu options
            with Container(id="menu-container", classes="content-box"):
                yield ListView(
                    MenuItem(1, "TITLE Keywords", "title_keywords"),
                    MenuItem(2, "Exact TITLE", "exact_title"),
                    MenuItem(3, "AUTHOR Browse", "author_browse"),
                    MenuItem(4, "SUBJECT Keywords", "subject_keywords"),
                    MenuItem(5, "SERIES", "series"),
                    MenuItem(6, "SUPER Search", "super_search"),
                    MenuItem(7, "ISBN Search", "isbn_search"),
                    MenuItem(8, "Settings", "settings"),
                    MenuItem(9, "About", "about"),
                    MenuItem(0, "Quit", "quit"),
                    id="main-menu",
                )
        
        # Status bar
        yield FooterBar(
            prompt="Enter your selection and press <Enter>:",
            shortcuts="1-9,0=Select, ?=Help, Q=Quit",
            id="status-bar"
        )
    
    def on_mount(self) -> None:
        """Focus the menu on mount."""
        menu = self.query_one("#main-menu", ListView)
        menu.focus()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle menu item selection."""
        item = event.item
        if isinstance(item, MenuItem):
            self._handle_action(item.action)
    
    def _handle_action(self, action: str) -> None:
        """Handle the selected menu action."""
        if action == "quit":
            self.app.exit()
        elif action == "title_keywords":
            self.app.push_screen("search", {"search_type": "title", "prompt": "TITLE Keyword"})
        elif action == "exact_title":
            self.app.push_screen("search", {"search_type": "title_exact", "prompt": "Exact TITLE"})
        elif action == "author_browse":
            self.app.push_screen("search", {"search_type": "author", "prompt": "AUTHOR"})
        elif action == "subject_keywords":
            self.app.push_screen("search", {"search_type": "subject", "prompt": "SUBJECT Keyword"})
        elif action == "series":
            self.app.push_screen("search", {"search_type": "series", "prompt": "SERIES"})
        elif action == "super_search":
            self.app.push_screen("search", {"search_type": "keyword", "prompt": "Keywords"})
        elif action == "isbn_search":
            self.app.push_screen("search", {"search_type": "isbn", "prompt": "ISBN"})
        elif action == "settings":
            self.app.push_screen("settings")
        elif action == "about":
            self.app.push_screen("about")
    
    def action_select_1(self) -> None:
        self._handle_action("title_keywords")
    
    def action_select_2(self) -> None:
        self._handle_action("exact_title")
    
    def action_select_3(self) -> None:
        self._handle_action("author_browse")
    
    def action_select_4(self) -> None:
        self._handle_action("subject_keywords")
    
    def action_select_5(self) -> None:
        self._handle_action("series")
    
    def action_select_6(self) -> None:
        self._handle_action("super_search")
    
    def action_select_7(self) -> None:
        self._handle_action("isbn_search")
    
    def action_select_8(self) -> None:
        self._handle_action("settings")
    
    def action_select_9(self) -> None:
        self._handle_action("about")
    
    def action_select_0(self) -> None:
        self._handle_action("quit")
    
    def action_quit_app(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help")
