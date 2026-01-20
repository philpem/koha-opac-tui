"""
Help text content for the Koha OPAC TUI.
Stored separately for easy maintenance.
"""

HELP_SECTIONS = {
    "main": {
        "title": "MAIN MENU",
        "content": """
From the main menu, select a search type:

  1. TITLE Keywords    - Search by words in the title
  2. Exact TITLE       - Search for exact title match
  3. AUTHOR Browse     - Search by author name
  4. SUBJECT Keywords  - Search by subject headings
  5. SERIES            - Search for book series
  6. SUPER Search      - Search all fields
  7. ISBN Search       - Search by ISBN number
  8. Settings          - Configure the application
  9. About             - About this application
  0. Quit              - Exit the application

Navigation:
  - Use number keys (0-9) for quick selection
  - Use arrow keys to highlight, Enter to select
  - Press Q or Esc to quit
"""
    },
    
    "search": {
        "title": "SEARCHING",
        "content": """
Enter your search terms and press Enter.

Tips:
  - Partial words are OK (e.g., "HEMINGW" for Hemingway)
  - Author searches work best as "Last, First"
  - ISBN searches accept both ISBN-10 and ISBN-13
  - Multiple words narrow your search

Navigation:
  - Esc = Go back to previous screen
  - Enter = Submit search
"""
    },
    
    "results": {
        "title": "SEARCH RESULTS",
        "content": """
Browse your search results:

  - Use arrow keys to move through results
  - Press Enter to view item details
  - Press a number (1-9, 0) to select that item

Pagination:
  - PgDn or N = Next page of results
  - PgUp or P = Previous page of results

Navigation:
  - Esc = Go back to search screen
"""
    },
    
    "detail": {
        "title": "ITEM DETAILS",
        "content": """
View bibliographic information and holdings:

The screen shows:
  - Top: Bibliographic details (title, author, etc.)
  - Bottom: Holdings table showing:
    * Library location
    * Call number / Shelfmark
    * Availability status
    * Due date (if on loan)

Navigation:
  - Use arrow keys to scroll holdings
  - Esc = Return to search results
"""
    },
}


def get_full_help_text() -> str:
    """Generate the complete help text."""
    lines = []
    lines.append("=" * 78)
    lines.append("KOHA OPAC TERMINAL - HELP".center(78))
    lines.append("=" * 78)
    lines.append("")
    
    for section_id, section in HELP_SECTIONS.items():
        lines.append(f"─── {section['title']} {'─' * (72 - len(section['title']))}")
        lines.append(section['content'].strip())
        lines.append("")
    
    lines.append("=" * 78)
    lines.append("Press Esc to return".center(78))
    lines.append("=" * 78)
    
    return "\n".join(lines)


def get_section_help(section: str) -> str:
    """Get help text for a specific section."""
    if section in HELP_SECTIONS:
        return HELP_SECTIONS[section]['content'].strip()
    return "No help available for this section."
