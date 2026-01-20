"""
Help text content for the Koha OPAC TUI.
Stored separately for easy maintenance.
"""

HELP_SECTIONS = {
    "main_menu": {
        "title": "MAIN MENU HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                              MAIN MENU HELP
══════════════════════════════════════════════════════════════════════════════

Select a search type to find items in the catalog:

  1. TITLE Keywords    - Search by words in the title
  2. Exact TITLE       - Search for exact title match
  3. Exact TITLE       - Search for exact title match
  3. AUTHOR Browse     - Search by author name (Last, First)
  4. SUBJECT Keywords  - Search by subject headings
  5. SERIES            - Search for book series
  6. SUPER Search      - Search all fields at once
  7. ISBN Search       - Search by ISBN number
  8. Settings          - Configure server and display options
  9. About             - Information about this application
  0. Quit              - Exit the application

NAVIGATION:
  Number Keys (0-9)    Quick-select a menu option
  Arrow Keys           Move highlight up/down
  Enter                Select highlighted option
  Q or Esc             Quit the application

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "search": {
        "title": "SEARCH HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                              SEARCH HELP
══════════════════════════════════════════════════════════════════════════════

Enter your search terms in the input field below.

SEARCH TIPS:
  • Partial words are OK (e.g., "HEMINGW" finds Hemingway)
  • Multiple words narrow your search
  • Searches are not case-sensitive

AUTHOR SEARCHES:
  • Use format: Last name, First name
  • Example: ASIMOV, ISAAC
  • Partial names work: ASIMOV or ASIM

ISBN SEARCHES:
  • Enter ISBN-10 or ISBN-13
  • Dashes are optional

NAVIGATION:
  Enter                Submit your search
  Esc                  Go back to main menu

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "results": {
        "title": "SEARCH RESULTS HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                           SEARCH RESULTS HELP
══════════════════════════════════════════════════════════════════════════════

Your search results are displayed in a list. Each entry shows:
  • Item number (for quick selection)
  • Author name and date
  • Title of the work

SELECTING AN ITEM:
  Number Keys (1-9, 0)  Select item by its number (0 = item 10)
  Arrow Keys            Move highlight up/down
  Enter                 View details of highlighted item

PAGINATION:
  PgDn or N             Next page of results
  PgUp or P             Previous page of results

NAVIGATION:
  Esc                   Go back to search screen

The status bar shows total results and current page number.

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "detail": {
        "title": "ITEM DETAILS HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                            ITEM DETAILS HELP
══════════════════════════════════════════════════════════════════════════════

This screen shows detailed information about the selected item.

UPPER SECTION - Bibliographic Details:
  • Title and author
  • Publication information
  • ISBN and call number
  • Physical description
  • Summary (if available)

LOWER SECTION - Item Holdings:
  Shows all copies of this item in the library system:
  
  Library        Which branch holds this copy
  Location       Where in the library (e.g., Adult Fiction)
  Call Number    Shelf location / Shelfmark
  Status         Available, On Loan, Reference Only, etc.
  Due Date       When an on-loan item is due back

NAVIGATION:
  Arrow Keys           Scroll through holdings table
  Esc                  Return to search results

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "settings": {
        "title": "SETTINGS HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                             SETTINGS HELP
══════════════════════════════════════════════════════════════════════════════

Configure the OPAC terminal settings:

CONNECTION SETTINGS:
  Koha Server URL      The web address of your Koha installation
                       Example: https://library.example.org
  
  Library Name         Displayed in the header bar

DISPLAY SETTINGS:
  Color Theme          Choose your preferred terminal colors:
                       • Amber  - Classic amber phosphor
                       • Green  - Green phosphor (VT100 style)
                       • White  - Monochrome white on black
                       • Blue   - Cool blue terminal
  
  Items per page       How many search results to show (default: 10)

BUTTONS:
  Save Settings        Save your changes
  Cancel               Discard changes and go back
  Test Connection      Verify the server is reachable

NAVIGATION:
  Tab                  Move between fields
  Esc                  Cancel and go back

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "about": {
        "title": "ABOUT",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                                 ABOUT
══════════════════════════════════════════════════════════════════════════════

                      KOHA OPAC TEXT TERMINAL
                          Version 1.0.0

A nostalgic text-based interface for the Koha Integrated Library System,
inspired by the classic Dynix and BLCMP library terminals of the 1990s.

This application connects to any Koha ILS via its REST API to provide:

  • Catalog searching by title, author, subject, ISBN, and more
  • Detailed bibliographic record viewing
  • Real-time item availability and holdings information
  • Classic terminal aesthetics with customizable color themes

Built with:
  • Textual - Modern TUI framework for Python
  • Koha REST API - Open source ILS

For more information about Koha: https://koha-community.org

══════════════════════════════════════════════════════════════════════════════
                      Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "general": {
        "title": "GENERAL HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                             GENERAL HELP
══════════════════════════════════════════════════════════════════════════════

KOHA OPAC TEXT TERMINAL - Quick Reference

GLOBAL KEYS:
  Esc                  Go back / Cancel / Quit
  ?                    Show help for current screen
  Arrow Keys           Navigate menus and lists
  Enter                Select / Confirm

MAIN MENU:
  1-9, 0               Quick-select menu options
  Q                    Quit application

SEARCH RESULTS:
  1-9, 0               Select result by number
  PgUp / PgDn          Previous / Next page
  N / P                Next / Previous page

TIPS:
  • The header shows date, library name, and current time
  • The footer shows available commands for each screen
  • Use --demo flag to test without a Koha server

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
}


def get_help_for_screen(screen_name: str) -> str:
    """Get help text for a specific screen."""
    if screen_name in HELP_SECTIONS:
        return HELP_SECTIONS[screen_name]['content']
    return HELP_SECTIONS['general']['content']


def get_help_title(screen_name: str) -> str:
    """Get the help title for a specific screen."""
    if screen_name in HELP_SECTIONS:
        return HELP_SECTIONS[screen_name]['title']
    return "HELP"


def get_full_help_text() -> str:
    """Generate the complete help text (all sections)."""
    return HELP_SECTIONS['general']['content']
