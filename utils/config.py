"""
Configuration management for the Koha OPAC TUI.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, List

from utils.validators import validate_url, validate_timeout, validate_items_per_page


CONFIG_DIR = Path.home() / ".config" / "koha-opac-tui"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class KohaConfig:
    """Configuration for connecting to a Koha instance."""
    
    # Server settings - must be configured for real use
    base_url: str = "https://your-koha-server.org"
    api_version: str = "v1"
    
    # Authentication (optional for public endpoints)
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # Display settings
    theme: str = "amber"
    library_name: str = "PUBLIC LIBRARY"
    opac_name: str = "Dial Pac"
    items_per_page: int = 10
    
    # Search results display
    # Whether to add blank line between results for readability
    result_spacing: bool = False
    
    # Call number display settings
    # Options: "lcc" (LOC only), "dewey" (Dewey only), "both" (show both)
    call_number_display: str = "both"
    # Terminology: "callnumber" or "shelfmark"
    call_number_label: str = "callnumber"
    
    # Demo mode - use mock data instead of real API
    demo_mode: bool = False
    
    # Timeout settings
    request_timeout: int = 30
    
    def get_call_number_label(self) -> str:
        """Get the label to use for call numbers based on settings."""
        if self.call_number_label == "shelfmark":
            return "Shelfmark"
        return "Call Number"
    
    def get_call_number_label_short(self) -> str:
        """Get the short label for call numbers (for table columns)."""
        if self.call_number_label == "shelfmark":
            return "Shelfmark"
        return "Call#"
    
    @property
    def public_api_url(self) -> str:
        """Get the public API base URL."""
        return f"{self.base_url.rstrip('/')}/api/{self.api_version}/public"
    
    @property
    def staff_api_url(self) -> str:
        """Get the staff API base URL."""
        return f"{self.base_url.rstrip('/')}/api/{self.api_version}"

    def validate(self) -> List[str]:
        """
        Validate configuration settings.

        Returns:
            List of error messages. Empty list if configuration is valid.

        Example:
            config = KohaConfig.load()
            errors = config.validate()
            if errors:
                for error in errors:
                    print(f"Configuration error: {error}")
        """
        errors = []

        # Validate base URL
        if not self.base_url or self.base_url == "https://your-koha-server.org":
            errors.append("base_url must be configured (currently set to default value)")
        else:
            is_valid, error_msg = validate_url(self.base_url)
            if not is_valid:
                errors.append(f"base_url is invalid: {error_msg}")

        # Validate timeout
        is_valid, error_msg = validate_timeout(self.request_timeout)
        if not is_valid:
            errors.append(f"request_timeout is invalid: {error_msg}")

        # Validate items per page
        is_valid, error_msg = validate_items_per_page(self.items_per_page)
        if not is_valid:
            errors.append(f"items_per_page is invalid: {error_msg}")

        # Validate call number display mode
        if self.call_number_display not in ("lcc", "dewey", "both"):
            errors.append(f"call_number_display must be 'lcc', 'dewey', or 'both', got: {self.call_number_display}")

        # Validate call number label
        if self.call_number_label not in ("callnumber", "shelfmark"):
            errors.append(f"call_number_label must be 'callnumber' or 'shelfmark', got: {self.call_number_label}")

        return errors

    def save(self) -> None:
        """Save configuration to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def load(cls) -> "KohaConfig":
        """Load configuration from file, or return defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()


def get_config() -> KohaConfig:
    """Get the current configuration."""
    return KohaConfig.load()
