"""
Help Screen - Displays keyboard shortcuts and usage instructions.
"""

from textual.app import ComposeResult
from textual.containers import Container, Center, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding


HELP_TEXT = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HELP - HOW TO USE                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

NAVIGATION
══════════════════════════════════════════════════════════════════════════════

  Arrow Keys      Move up/down through menus and results
  Enter           Select highlighted item
  Number Keys     Quick-select menu option (1-9, 0)
  Escape or B     Go back to previous screen
  Q               Quit application (from main menu)

MAIN MENU
══════════════════════════════════════════════════════════════════════════════

  From the main menu, you can access different search types:
  
  1. TITLE Keywords    - Search for books by words in the title
  2. Exact TITLE       - Search for an exact title match
  3. AUTHOR Browse     - Search by author name (Last, First)
  4. SUBJECT Keywords  - Search by subject headings
  5. SERIES            - Search for book series
  6. SUPER Search      - Search across all fields
  7. ISBN Search       - Search by ISBN number
  8. Settings          - Configure server and display settings
  9. About             - Information about this application
  0. Quit              - Exit the application

SEARCHING
══════════════════════════════════════════════════════════════════════════════

  • Type your search terms and press Enter
  • Partial words are accepted (e.g., "HEMINGW" for Hemingway)
  • Author searches work best as "Last, First" format
  • ISBN searches accept both ISBN-10 and ISBN-13 formats

  Commands while searching:
    SO               Start Over (return to main menu)
    B                Go Back to previous screen

SEARCH RESULTS
══════════════════════════════════════════════════════════════════════════════

  • Use arrow keys or number keys to select a result
  • Press Enter to view full details of selected item
  
  Commands:
    N or Page Down   Next page of results
    P or Page Up     Previous page of results
    B or Escape      Go back to search screen
    Number (1-9, 0)  Select item by number

ITEM DETAILS
══════════════════════════════════════════════════════════════════════════════

  The detail screen shows:
  
  Top Section:     Bibliographic information (title, author, ISBN, etc.)
  Bottom Section:  Holdings table showing:
                   - Library location
                   - Call number/Shelfmark  
                   - Current availability status
                   - Due date (if on loan)

  • Use arrow keys to scroll through holdings
  • Press B or Escape to return to results

SETTINGS
══════════════════════════════════════════════════════════════════════════════

  Configure:
  • Koha server URL (your library's Koha installation)
  • Library name (displayed in header)
  • Color theme (Amber, Green, White, Blue)
  • Items per page

  Press "Test Connection" to verify your server settings.

╔══════════════════════════════════════════════════════════════════════════════╗
║              Press Escape or any key to return to previous screen            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""


class HelpScreen(Screen):
    """
    Help screen showing usage instructions and keyboard shortcuts.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("q", "go_back", "Back", show=False),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with ScrollableContainer(id="help-container"):
            yield Static(HELP_TEXT, id="help-text")
    
    def action_go_back(self) -> None:
        """Go back to previous screen."""
        self.app.pop_screen()
