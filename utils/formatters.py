"""
Formatting utilities for bibliographic records.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.client import BiblioRecord
    from utils.config import KohaConfig

# Display formatting constants
MAX_SUBJECTS_DISPLAY = 3  # Maximum number of subject headings to show
SUMMARY_MAX_LENGTH = 120  # Maximum length for summary in compact view
ELLIPSIS = "..."  # Truncation indicator


def format_biblio_details(
    record: "BiblioRecord",
    config: "KohaConfig",
    include_extended: bool = True,
) -> str:
    """
    Format a bibliographic record for display.

    Args:
        record: The bibliographic record to format.
        config: Application configuration for call number display settings.
        include_extended: If True, include edition, physical description,
                         series, subjects, and summary. If False, only
                         include basic fields (title, author, publication, ISBN,
                         call numbers).

    Returns:
        Formatted string representation of the record.
    """
    lines = []

    # Title
    title = record.title or "Unknown Title"
    lines.append(f"{'Title:':<12}{title}")

    # Author
    if record.author:
        lines.append(f"{'Author:':<12}{record.author}")

    # Publication info
    pub_parts = []
    if record.publisher:
        pub_parts.append(record.publisher)
    if record.publication_year:
        pub_parts.append(record.publication_year)
    if pub_parts:
        lines.append(f"{'Published:':<12}{', '.join(pub_parts)}")

    # ISBN
    if record.isbn:
        lines.append(f"{'ISBN:':<12}{record.isbn}")

    # Call Number(s) - based on display settings
    call_label = "Call No."
    display_mode = config.call_number_display

    call_parts = []
    if display_mode == "both":
        if record.call_number_lcc:
            call_parts.append(f"LOC: {record.call_number_lcc}")
        if record.call_number_dewey:
            call_parts.append(f"DDC: {record.call_number_dewey}")
        if call_parts:
            lines.append(f"{call_label + ':':<12}{' | '.join(call_parts)}")
        elif record.call_number:
            lines.append(f"{call_label + ':':<12}{record.call_number}")
    elif display_mode == "lcc":
        cn = record.call_number_lcc or record.call_number
        if cn:
            lines.append(f"{call_label + ':':<12}{cn}")
    elif display_mode == "dewey":
        cn = record.call_number_dewey or record.call_number
        if cn:
            lines.append(f"{call_label + ':':<12}{cn}")

    # Extended fields (optional)
    if include_extended:
        # Edition
        if record.edition:
            lines.append(f"{'Edition:':<12}{record.edition}")

        # Physical description
        if record.physical_description:
            lines.append(f"{'Physical:':<12}{record.physical_description}")

        # Series
        if record.series:
            lines.append(f"{'Series:':<12}{record.series}")

        # Subjects (first few with ellipsis if more)
        if record.subjects:
            subjects_str = "; ".join(record.subjects[:MAX_SUBJECTS_DISPLAY])
            if len(record.subjects) > MAX_SUBJECTS_DISPLAY:
                subjects_str += ELLIPSIS
            lines.append(f"{'Subjects:':<12}{subjects_str}")

        # Summary (truncated for compact display)
        if record.summary:
            summary = record.summary
            if len(summary) > SUMMARY_MAX_LENGTH:
                summary = summary[:SUMMARY_MAX_LENGTH - len(ELLIPSIS)] + ELLIPSIS
            lines.append(f"{'Summary:':<12}{summary}")

    return "\n".join(lines)
