# Koha OPAC TUI

A nostalgic text-based user interface (TUI) for the Koha Integrated Library System, inspired by the classic Dynix and BLCMP library terminals of the 1990s and early 2000s.

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
python app.py
```

### Command Line Options

```bash
python app.py --theme amber    # Use amber phosphor theme
python app.py --theme green    # Use green phosphor theme
python app.py --theme white    # Use white on black theme
python app.py --theme blue     # Use blue terminal theme

python app.py --server https://your-koha-server.org
python app.py --library "Your Library Name"
```

### Keyboard Shortcuts

#### Main Menu
| Key | Action |
|-----|--------|
| 1-9, 0 | Quick select menu option |
| ↑/↓ | Navigate menu items |
| Enter | Select highlighted item |
| Q | Quit application |
| ? | Show help |

#### Search Screen
| Key | Action |
|-----|--------|
| Enter | Submit search |
| Escape | Go back |
| Type "SO" | Start over (main menu) |
| Type "B" | Go back |

#### Search Results
| Key | Action |
|-----|--------|
| 1-9, 0 | Select result by number |
| ↑/↓ | Navigate results |
| Enter | View selected item details |
| N / Page Down | Next page |
| P / Page Up | Previous page |
| B / Escape | Go back |

#### Item Detail
| Key | Action |
|-----|--------|
| ↑/↓ | Scroll holdings table |
| B / Escape | Go back to results |

## Configuration

Settings are stored in `~/.config/koha-opac-tui/config.json` and include:

- **base_url**: Your Koha server URL
- **library_name**: Name displayed in the header
- **theme**: Color theme (amber, green, white, blue)
- **items_per_page**: Number of search results per page

You can configure these settings through the Settings menu (option 8) or by editing the config file directly.

## Color Themes

The application includes four classic terminal color themes:

### Amber (Default)
Classic amber phosphor monitor look, reminiscent of IBM 3278 terminals.

### Green
Green phosphor (P1) terminal style, like the classic VT100.

### White
Clean monochrome white-on-black display.

### Blue
Cool blue terminal aesthetic.

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

## Troubleshooting

### Connection Issues

1. Verify your Koha server URL is correct
2. Check that the Koha REST API is enabled
3. Use the "Test Connection" button in Settings
4. Ensure your network allows connections to the server

### No Search Results

- The Koha public API may have limited search capabilities
- Try broader search terms
- Verify the catalog has records

### Display Issues

- Ensure your terminal supports Unicode characters
- Try a different terminal emulator
- Adjust terminal font size if text appears cramped

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

- **Koha Community** - For the excellent open source ILS
- **Textual** - For the modern Python TUI framework
- **Dynix/SirsiDynix** - Inspiration from their classic terminal interfaces
- **BLCMP** - For their pioneering library automation systems

## History

In the 1990s and early 2000s, library patrons would use text-based terminals to search the catalog. These systems, with their distinctive amber or green screens, became iconic symbols of library technology. This project aims to recreate that experience while connecting to modern library systems.

---

*"Press any key to continue..."*
