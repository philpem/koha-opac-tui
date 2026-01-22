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
  • Title and author (contributors shown with |)
  • Publication information
  • ISBN and call numbers (LOC/Dewey on one line)
  • Edition, physical description, series
  • Summary (truncated - press F for full view)

LOWER SECTION - Item Holdings:
  Shows copies of this item in the library system:
  
  Library        Which branch holds this copy
  Location       Where in the library (e.g., Adult Fiction)
  Call Number    Shelf location / Shelfmark
  Status         Available, On Loan, Reference Only, etc.
  Due Date       When an on-loan item is due back
  Note           Public notes about this copy

COMMANDS:
  Enter                View holding details for selected library
  F                    View full bibliographic details (no holdings)
  Arrow Keys           Scroll through holdings table
  Esc                  Return to search results

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "full_biblio": {
        "title": "FULL BIBLIOGRAPHIC DETAILS HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                     FULL BIBLIOGRAPHIC DETAILS HELP
══════════════════════════════════════════════════════════════════════════════

This screen shows the complete bibliographic record without the holdings table.

INFORMATION DISPLAYED:
  • Title - Full title including subtitle
  • Author - Main author and all contributors
  • Publisher - Place and name of publisher
  • Year - Publication year
  • ISBN - International Standard Book Number
  • Call Numbers - LOC and/or Dewey classifications
  • Edition - Edition statement
  • Physical - Pages, dimensions, etc.
  • Series - Series title if part of a series
  • Subjects - Subject headings
  • Notes - General notes
  • Summary - Full summary/abstract
  • Record ID - Internal bibliographic record number

Use the arrow keys to scroll through long records.

NAVIGATION:
  Arrow Keys           Scroll up/down
  Esc                  Return to item details

══════════════════════════════════════════════════════════════════════════════
                         Press Esc to return
══════════════════════════════════════════════════════════════════════════════
"""
    },
    
    "holding_detail": {
        "title": "HOLDING DETAILS HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                          HOLDING DETAILS HELP
══════════════════════════════════════════════════════════════════════════════

This screen shows detailed information about holdings at a specific library.

SECTIONS:

  BIBLIOGRAPHIC DETAILS
    Title, author, publication info, ISBN, and call numbers.

  HOLDINGS AT [LIBRARY NAME]
    All copies held by this library, showing:
      Copy         Copy number
      Location     Where in the library
      Call Number  Shelf location / Shelfmark
      Barcode      Item barcode
      Status       Available, On Loan, etc.
      Due Date     When an on-loan item is due back

  ITEM DETAILS
    Full details for the currently selected copy:
      Library, Location, Call Number, Copy Number,
      Barcode, Item Type, Status, Due Date, and Notes.

NAVIGATION:
  Arrow Keys           Select different copies in the table
  Esc                  Return to item details

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
    
    "marc_detail": {
        "title": "MARC RECORD HELP",
        "content": """
══════════════════════════════════════════════════════════════════════════════
                             MARC RECORD HELP
══════════════════════════════════════════════════════════════════════════════

This screen displays the full MARC (Machine-Readable Cataloging) record
with field descriptions.

MARC STRUCTURE:
  • Leader (LDR)       Record metadata and type information
  • 00X fields         Control fields (no subfields)
  • 0XX-9XX fields     Variable fields with subfields

COMMON FIELDS:
  020   ISBN                 245   Title Statement
  050   LC Call Number       250   Edition
  082   Dewey Call Number    260   Publication Info
  100   Main Author          300   Physical Description
  650   Subject Headings     700   Additional Authors

SUBFIELDS:
  Each field may contain subfields marked with $
  Example: $a = main data, $b = subtitle, $c = responsibility

NAVIGATION:
  Arrow Keys / Scroll    Move through the record
  Esc                    Return to item details

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
