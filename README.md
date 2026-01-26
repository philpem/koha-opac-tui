# Koha OPAC TUI

A text-mode user interface to interact with the Koha ILS, based on the classic Dynix and BLCMP library terminal interface.

This has been "vibe coded" with Claude AI as an experiment. It probably would have been quicker to write it from scratch...

## Features

- **Classic Terminal Aesthetics**: Reminiscent of the amber and green phosphor terminals found in libraries during the 1990s
- **Full Catalog Search**: Search by title, author, subject, ISBN, series, and more
- **Real-time Holdings Display**: View item availability, location, and due dates
- **Customizable Themes**: Choose from amber, green, white, or blue color schemes
- **Keyboard Navigation**: Efficient number-key shortcuts for quick navigation
- **Koha REST API Integration**: Connects to any Koha ILS instance

## Installation

### Prerequisites

- Python 3.9 or higher
- Access to a Koha ILS server with the REST API enabled

### Install from Source

```bash
# Clone or download the repository
cd koha-opac-tui

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
# Run with demo mode (uses sample data, no server needed)
python app.py --demo

# Run with a real Koha server
python app.py --server https://your-koha-server.org
```

### Demo servers

The following public Koha ILS demo servers currently work with this, and can be used to test:

  * http://demo.kohacatalog.com/

There is also a demonstration mode which uses local test data.

### Command Line Options

```bash
python app.py --demo              # Use demo mode with sample data
python app.py --theme amber       # Use amber phosphor theme
python app.py --theme green       # Use green phosphor theme  
python app.py --theme white       # Use white on black theme
python app.py --theme blue        # Use blue terminal theme

python app.py --server https://your-koha-server.org
python app.py --library "Your Library Name"
python app.py --call-number-display both    # Show both LOC and Dewey
python app.py --call-number-display lcc     # Show LOC only
python app.py --call-number-display dewey   # Show Dewey only
python app.py --call-number-label shelfmark # Use "Shelfmark" instead of "Call Number"
```

### Keyboard Shortcuts

#### Main Menu
| Key | Action |
|-----|--------|
| 1-9, 0 | Quick select menu option |
| ↑/↓ | Navigate menu items |
| Enter | Select highlighted item |
| Q / Esc | Quit application |
| F1 | Show help |

#### Search Screen
| Key | Action |
|-----|--------|
| Enter | Submit search |
| Escape | Go back |
| F1 | Show help |

#### Search Results
| Key | Action |
|-----|--------|
| 1-9, 0 | Select result by number |
| ↑/↓ | Navigate results |
| Enter | View selected item details |
| Escape | Go back |
| F1 | Show help |

#### Item Detail
| Key | Action |
|-----|--------|
| ↑/↓ | Scroll holdings table |
| F | Full bibliographic details |
| M | MARC record view |
| Escape | Go back to results |
| F1 | Show help |

## Configuration

Configuration is stored in `~/.config/koha-opac-tui/config.json`.

### Library Administrator Settings

These are typically set via command line or config file, not by patrons:

| Setting | Description | Default |
|---------|-------------|---------|
| `base_url` | Koha server URL | `https://your-koha-server.org` |
| `library_name` | Name displayed in header | `PUBLIC LIBRARY` |
| `call_number_display` | Which call numbers to show: `both`, `lcc`, or `dewey` | `both` |
| `call_number_label` | Terminology: `callnumber` or `shelfmark` | `callnumber` |

### User Preferences

These can be changed by patrons in the Settings menu:

| Setting | Description | Default |
|---------|-------------|---------|
| `theme` | Color theme: `amber`, `green`, `white`, `blue` | `amber` |
| `result_spacing` | Add blank lines between search results | `false` |

### Example Config File

```json
{
  "base_url": "https://opac.mylibrary.org",
  "library_name": "MY PUBLIC LIBRARY",
  "theme": "amber",
  "call_number_display": "dewey",
  "call_number_label": "shelfmark",
  "result_spacing": false
}
```

## Color Themes

The application includes four classic terminal color themes:

  * Amber (Default). Classic amber phosphor monitor look.
  * Green (P1 phosphor) terminal style.
  * White. Clean monochrome white-on-black display.
  * Blue. Cool blue, just as a treat.

## Project Structure

```
koha-opac-tui/
├── app.py              # Main application entry point
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── api/
│   ├── __init__.py
│   └── client.py      # Koha REST API client
├── screens/
│   ├── __init__.py
│   ├── main_menu.py   # Main menu screen
│   ├── search.py      # Search input screen
│   ├── results.py     # Search results screen
│   ├── detail.py      # Item detail screen
│   ├── settings.py    # Settings configuration
│   ├── about.py       # About screen
│   └── help.py        # Help screen
├── utils/
│   ├── __init__.py
│   ├── config.py      # Configuration management
│   └── themes.py      # Terminal color themes
└── widgets/
    └── __init__.py    # Custom widgets (future)
```

## Koha API Requirements

This application uses the Koha REST API public endpoints:

- `GET /api/v1/public/biblios` - Search and retrieve bibliographic records
- `GET /api/v1/public/biblios/{id}` - Get a specific record
- `GET /api/v1/public/biblios/{id}/items` - Get item holdings
- `GET /api/v1/public/libraries` - Get library information

Ensure your Koha installation has:
1. The REST API enabled (`RESTPublicAPI` system preference)
2. Public endpoints accessible

The OPAC web interface is also used to run searches, because the "biblios" endpoint often doesn't work as documented for this.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open source. See LICENSE file for details.

---

*"Press any key to continue..."*
