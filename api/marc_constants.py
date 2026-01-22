"""
MARC 21 field constants for bibliographic records.

This module defines constants for commonly used MARC 21 field tags
to improve code readability and maintainability throughout the API client.

MARC 21 Format for Bibliographic Data:
https://www.loc.gov/marc/bibliographic/
"""

# Control Fields (00X)
MARC_FIELD_CONTROL_NUMBER = "001"
MARC_FIELD_CONTROL_NUMBER_ID = "003"
MARC_FIELD_DATE_AND_TIME = "005"
MARC_FIELD_FIXED_LENGTH_DATA = "008"

# ISBN and Standard Numbers (01X-04X)
MARC_FIELD_ISBN = "020"
MARC_FIELD_ISSN = "022"
MARC_FIELD_LCCN = "010"

# Classification Numbers (05X-08X)
MARC_FIELD_LC_CALL_NUMBER = "050"
MARC_FIELD_DEWEY_DECIMAL = "082"
MARC_FIELD_LOCAL_CALL_NUMBER = "090"

# Main Entry Fields (1XX)
MARC_FIELD_MAIN_AUTHOR_PERSONAL = "100"
MARC_FIELD_MAIN_AUTHOR_CORPORATE = "110"
MARC_FIELD_MAIN_AUTHOR_MEETING = "111"

# Title and Title-Related Fields (20X-24X)
MARC_FIELD_TITLE = "245"
MARC_FIELD_EDITION = "250"
MARC_FIELD_PUBLICATION_OLD = "260"  # Older MARC records
MARC_FIELD_PUBLICATION_RDA = "264"  # RDA (Resource Description and Access) records

# Physical Description (3XX)
MARC_FIELD_PHYSICAL_DESCRIPTION = "300"

# Series Statement (4XX)
MARC_FIELD_SERIES = "490"

# Notes (5XX)
MARC_FIELD_GENERAL_NOTE = "500"
MARC_FIELD_SUMMARY = "520"

# Subject Access Fields (6XX)
MARC_FIELD_SUBJECT_TOPICAL = "650"
MARC_FIELD_SUBJECT_GEOGRAPHIC = "651"

# Added Entry Fields (7XX)
MARC_FIELD_ADDED_AUTHOR_PERSONAL = "700"
MARC_FIELD_ADDED_AUTHOR_CORPORATE = "710"

# Series Added Entry (8XX)
MARC_FIELD_SERIES_ADDED_ENTRY = "830"

# Common Subfield Codes
# These are consistent across many fields but their meaning may vary
SUBFIELD_MAIN_ENTRY = "a"
SUBFIELD_REMAINDER = "b"
SUBFIELD_STATEMENT_OF_RESPONSIBILITY = "c"
SUBFIELD_DATE = "d"

# Title-specific subfields (245)
TITLE_SUBFIELD_TITLE = "a"
TITLE_SUBFIELD_SUBTITLE = "b"
TITLE_SUBFIELD_RESPONSIBILITY = "c"

# Publication-specific subfields (260/264)
PUB_SUBFIELD_PLACE = "a"
PUB_SUBFIELD_PUBLISHER = "b"
PUB_SUBFIELD_DATE = "c"

# Call number-specific subfields (050/082)
CALL_SUBFIELD_NUMBER = "a"
CALL_SUBFIELD_CUTTER = "b"

# Physical description subfields (300)
PHYS_SUBFIELD_EXTENT = "a"
PHYS_SUBFIELD_OTHER_DETAILS = "b"
PHYS_SUBFIELD_DIMENSIONS = "c"
