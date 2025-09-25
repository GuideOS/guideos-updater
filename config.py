"""
Configuration settings for GUP Update Manager
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "GUP Update Manager"
APP_VERSION = "1.0.0"

# Directories
CONFIG_DIR = Path.home() / '.config' / 'gup'
CACHE_DIR = Path.home() / '.cache' / 'gup'
LOG_DIR = Path.home() / '.local' / 'share' / 'gup'

# Create directories if they don't exist
for directory in [CONFIG_DIR, CACHE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# PolicyKit settings
USE_POLICYKIT = True  # Set to False to always use sudo
POLICYKIT_FOR_CACHE_UPDATE = True  # Use PolicyKit for cache updates (no password prompt)
POLICYKIT_FOR_INSTALL = True  # Use PolicyKit for installations

# Update settings  
AUTO_SELECT_ALL_UPDATES = True  # Select all updates by default
REFRESH_AFTER_INSTALL = True  # Auto-refresh after successful installation
CACHE_UPDATE_INTERVAL = 3600  # Seconds (1 hour)

# UI settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SHOW_NOTIFICATIONS = True

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB