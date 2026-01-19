"""
Configuration management for the Koha OPAC TUI.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".config" / "koha-opac-tui"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class KohaConfig:
    """Configuration for connecting to a Koha instance."""
    
    # Server settings
    base_url: str = "https://demo.koha-community.org"
    api_version: str = "v1"
    
    # Authentication (optional for public endpoints)
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    
    # Display settings
    theme: str = "amber"
    library_name: str = "PUBLIC LIBRARY"
    items_per_page: int = 10
    
    # Timeout settings
    request_timeout: int = 30
    
    @property
    def public_api_url(self) -> str:
        """Get the public API base URL."""
        return f"{self.base_url.rstrip('/')}/api/{self.api_version}/public"
    
    @property
    def staff_api_url(self) -> str:
        """Get the staff API base URL."""
        return f"{self.base_url.rstrip('/')}/api/{self.api_version}"
    
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
