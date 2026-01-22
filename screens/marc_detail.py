"""
MARC Detail Screen - Display full MARC record with field descriptions.
"""

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.screen import Screen
from textual.widgets import Static
from textual.binding import Binding

from api import BiblioRecord
from utils.config import KohaConfig
from widgets import HeaderBar, FooterBar


# MARC field descriptions - common fields used in library catalogs
MARC_FIELD_DESCRIPTIONS = {
    "001": "Control Number",
    "003": "Control Number Identifier",
    "005": "Date/Time of Latest Transaction",
    "006": "Fixed-Length Data Elements",
    "007": "Physical Description Fixed Field",
    "008": "Fixed-Length Data Elements",
    "010": "Library of Congress Control Number",
    "015": "National Bibliography Number",
    "016": "National Bibliographic Agency Control Number",
    "017": "Copyright Registration Number",
    "020": "International Standard Book Number (ISBN)",
    "022": "International Standard Serial Number (ISSN)",
    "024": "Other Standard Identifier",
    "028": "Publisher or Distributor Number",
    "035": "System Control Number",
    "037": "Source of Acquisition",
    "040": "Cataloging Source",
    "041": "Language Code",
    "042": "Authentication Code",
    "043": "Geographic Area Code",
    "044": "Country of Publishing Code",
    "045": "Time Period of Content",
    "050": "Library of Congress Call Number",
    "055": "Classification Numbers (Canadian)",
    "060": "National Library of Medicine Call Number",
    "070": "National Agricultural Library Call Number",
    "080": "Universal Decimal Classification Number",
    "082": "Dewey Decimal Classification Number",
    "084": "Other Classification Number",
    "086": "Government Document Classification Number",
    "090": "Local Call Number (LOC)",
    "092": "Local Call Number (Dewey)",
    "100": "Main Entry - Personal Name",
    "110": "Main Entry - Corporate Name",
    "111": "Main Entry - Meeting Name",
    "130": "Main Entry - Uniform Title",
    "210": "Abbreviated Title",
    "222": "Key Title",
    "240": "Uniform Title",
    "242": "Translation of Title",
    "243": "Collective Uniform Title",
    "245": "Title Statement",
    "246": "Varying Form of Title",
    "247": "Former Title",
    "250": "Edition Statement",
    "254": "Musical Presentation Statement",
    "255": "Cartographic Mathematical Data",
    "256": "Computer File Characteristics",
    "257": "Country of Producing Entity",
    "260": "Publication, Distribution (Imprint)",
    "263": "Projected Publication Date",
    "264": "Production, Publication, Distribution",
    "300": "Physical Description",
    "306": "Playing Time",
    "310": "Current Publication Frequency",
    "321": "Former Publication Frequency",
    "336": "Content Type",
    "337": "Media Type",
    "338": "Carrier Type",
    "340": "Physical Medium",
    "362": "Dates of Publication",
    "400": "Series Statement/Added Entry - Personal Name",
    "410": "Series Statement/Added Entry - Corporate Name",
    "411": "Series Statement/Added Entry - Meeting Name",
    "440": "Series Statement/Added Entry - Title",
    "490": "Series Statement",
    "500": "General Note",
    "501": "With Note",
    "502": "Dissertation Note",
    "504": "Bibliography Note",
    "505": "Formatted Contents Note",
    "506": "Restrictions on Access Note",
    "508": "Creation/Production Credits Note",
    "510": "Citation/References Note",
    "511": "Participant or Performer Note",
    "515": "Numbering Peculiarities Note",
    "516": "Type of Computer File Note",
    "518": "Date/Time and Place of Event Note",
    "520": "Summary, Etc.",
    "521": "Target Audience Note",
    "522": "Geographic Coverage Note",
    "524": "Preferred Citation of Described Materials",
    "525": "Supplement Note",
    "526": "Study Program Information Note",
    "530": "Additional Physical Form Available Note",
    "533": "Reproduction Note",
    "534": "Original Version Note",
    "535": "Location of Originals/Duplicates Note",
    "538": "System Details Note",
    "540": "Terms Governing Use and Reproduction",
    "541": "Immediate Source of Acquisition Note",
    "542": "Information Relating to Copyright Status",
    "544": "Location of Other Archival Materials",
    "545": "Biographical or Historical Data",
    "546": "Language Note",
    "547": "Former Title Complexity Note",
    "550": "Issuing Body Note",
    "555": "Cumulative Index/Finding Aids Note",
    "556": "Information About Documentation Note",
    "561": "Ownership and Custodial History",
    "562": "Copy and Version Identification Note",
    "563": "Binding Information",
    "580": "Linking Entry Complexity Note",
    "581": "Publications About Described Materials",
    "583": "Action Note",
    "584": "Accumulation and Frequency of Use Note",
    "585": "Exhibitions Note",
    "586": "Awards Note",
    "588": "Source of Description Note",
    "600": "Subject Added Entry - Personal Name",
    "610": "Subject Added Entry - Corporate Name",
    "611": "Subject Added Entry - Meeting Name",
    "630": "Subject Added Entry - Uniform Title",
    "648": "Subject Added Entry - Chronological Term",
    "650": "Subject Added Entry - Topical Term",
    "651": "Subject Added Entry - Geographic Name",
    "653": "Index Term - Uncontrolled",
    "654": "Subject Added Entry - Faceted Topical Term",
    "655": "Index Term - Genre/Form",
    "656": "Index Term - Occupation",
    "657": "Index Term - Function",
    "658": "Index Term - Curriculum Objective",
    "662": "Subject Added Entry - Hierarchical Place Name",
    "700": "Added Entry - Personal Name",
    "710": "Added Entry - Corporate Name",
    "711": "Added Entry - Meeting Name",
    "720": "Added Entry - Uncontrolled Name",
    "730": "Added Entry - Uniform Title",
    "740": "Added Entry - Uncontrolled Related Title",
    "751": "Added Entry - Geographic Name",
    "752": "Added Entry - Hierarchical Place Name",
    "753": "System Details Access to Computer Files",
    "754": "Added Entry - Taxonomic Identification",
    "760": "Main Series Entry",
    "762": "Subseries Entry",
    "765": "Original Language Entry",
    "767": "Translation Entry",
    "770": "Supplement/Special Issue Entry",
    "772": "Supplement Parent Entry",
    "773": "Host Item Entry",
    "774": "Constituent Unit Entry",
    "775": "Other Edition Entry",
    "776": "Additional Physical Form Entry",
    "777": "Issued With Entry",
    "780": "Preceding Entry",
    "785": "Succeeding Entry",
    "786": "Data Source Entry",
    "787": "Other Relationship Entry",
    "800": "Series Added Entry - Personal Name",
    "810": "Series Added Entry - Corporate Name",
    "811": "Series Added Entry - Meeting Name",
    "830": "Series Added Entry - Uniform Title",
    "841": "Holdings Coded Data Values",
    "842": "Textual Physical Form Designator",
    "843": "Reproduction Note",
    "844": "Name of Unit",
    "845": "Terms Governing Use and Reproduction",
    "850": "Holding Institution",
    "852": "Location",
    "853": "Captions and Pattern - Basic Bibliographic Unit",
    "856": "Electronic Location and Access",
    "863": "Enumeration and Chronology - Basic Bibliographic Unit",
    "866": "Textual Holdings - Basic Bibliographic Unit",
    "876": "Item Information - Basic Bibliographic Unit",
    "880": "Alternate Graphic Representation",
    "886": "Foreign MARC Information Field",
    "887": "Non-MARC Information Field",
    "900": "Local Data (Various)",
    "942": "Koha Item Type",
    "952": "Koha Holdings Data",
    "999": "System Control Numbers (Local)",
}

# Subfield code descriptions for common fields
SUBFIELD_DESCRIPTIONS = {
    "a": "Main entry/data",
    "b": "Remainder/subdivision",
    "c": "Qualifying information",
    "d": "Dates",
    "e": "Relator term",
    "f": "Date of work",
    "g": "Miscellaneous",
    "h": "Medium",
    "i": "Relationship",
    "j": "Attribution qualifier",
    "k": "Form subheading",
    "l": "Language",
    "m": "Medium of performance",
    "n": "Number of part",
    "o": "Arranged statement",
    "p": "Name of part",
    "q": "Fuller form of name",
    "r": "Key",
    "s": "Version",
    "t": "Title",
    "u": "Affiliation/URI",
    "v": "Volume/sequence",
    "w": "Control subfield",
    "x": "ISSN",
    "y": "Link text",
    "z": "Public note",
    "0": "Authority record control number",
    "1": "Real World Object URI",
    "2": "Source",
    "3": "Materials specified",
    "4": "Relationship",
    "5": "Institution",
    "6": "Linkage",
    "7": "Control subfield",
    "8": "Field link",
    "9": "Local data",
}


class MarcDetailScreen(Screen):
    """
    MARC record detail screen.
    Shows the full MARC record with field descriptions.
    """
    
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("f1", "show_help", "Help"),
    ]
    
    def __init__(self, config: KohaConfig, record: BiblioRecord, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.record = record
    
    def compose(self) -> ComposeResult:
        """Compose the MARC detail screen layout."""
        yield HeaderBar(
            library_name=self.config.library_name,
            opac_name="MARC View",
            id="header"
        )
        
        with Container(id="main-content"):
            with VerticalScroll(id="marc-scroll"):
                yield Static(self._format_marc_record(), id="marc-details")
        
        yield FooterBar(
            shortcuts="F1=Help, Esc=Back",
            id="status-bar"
        )
    
    def _format_marc_record(self) -> str:
        """Format the full MARC record for display."""
        if not self.record or not self.record.raw_data:
            return "MARC record data not available.\n\nThis may happen if the record was loaded from the OPAC HTML\ninstead of the API."
        
        lines = []
        lines.append("MARC RECORD")
        lines.append("=" * 70)
        lines.append(f"Record #{self.record.biblio_id}: {self.record.title}")
        lines.append("")
        
        # Get the MARC fields from raw_data
        marc_fields = self.record.raw_data.get("fields", [])
        
        if not marc_fields:
            lines.append("No MARC fields found in record data.")
            return "\n".join(lines)
        
        # Also include leader if present
        leader = self.record.raw_data.get("leader", "")
        if leader:
            lines.append(f"{'LDR':<5} {'Leader':<45}")
            lines.append(f"      {leader}")
            lines.append("")
        
        # Process each MARC field
        for field_obj in marc_fields:
            for tag, field_data in field_obj.items():
                # Get field description
                field_desc = MARC_FIELD_DESCRIPTIONS.get(tag, "")
                
                # Format the tag and description header
                if field_desc:
                    lines.append(f"{tag:<5} {field_desc}")
                else:
                    lines.append(f"{tag:<5}")
                
                # Handle control fields (00X) - they're just strings
                if isinstance(field_data, str):
                    lines.append(f"      {field_data}")
                
                # Handle variable fields with indicators and subfields
                elif isinstance(field_data, dict):
                    # Get indicators
                    ind1 = field_data.get("ind1", " ")
                    ind2 = field_data.get("ind2", " ")
                    
                    # Display indicators if not blank
                    if ind1.strip() or ind2.strip():
                        lines.append(f"      Indicators: [{ind1}][{ind2}]")
                    
                    # Process subfields
                    subfields = field_data.get("subfields", [])
                    for sf in subfields:
                        for code, value in sf.items():
                            sf_desc = SUBFIELD_DESCRIPTIONS.get(code, "")
                            if sf_desc:
                                lines.append(f"      ${code} ({sf_desc}): {value}")
                            else:
                                lines.append(f"      ${code}: {value}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def action_go_back(self) -> None:
        """Go back to the detail screen."""
        self.app.pop_screen()
    
    def action_show_help(self) -> None:
        """Show help screen."""
        self.app.push_screen("help", {"context": "marc_detail"})
