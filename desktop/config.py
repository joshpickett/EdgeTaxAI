# config.py - Streamlit Desktop Configuration

from pathlib import Path
import os
from typing import Dict, Any

# Import shared configuration
from api.config import SHARED_CONFIG

# ---- API Configuration ----
API_CONFIG = {
    "BASE_URL": os.getenv("API_BASE_URL", "http://localhost:5000/api"),
    "VERSION": SHARED_CONFIG["API_VERSION"],
    "TIMEOUT": SHARED_CONFIG["DEFAULT_TIMEOUT"],
    "RETRY_ATTEMPTS": SHARED_CONFIG["RETRY_ATTEMPTS"],
    "HEADERS": {"Content-Type": "application/json"},
}

# Platform-specific settings
PLATFORM_CONFIG = {
    "SYNC_SETTINGS": {
        "AUTO_SYNC": True,
        "SYNC_INTERVAL": 3600,  # 1 hour
        "BATCH_SIZE": 100,
    },
    "UI_SETTINGS": {"THEME": "light", "ANIMATIONS_ENABLED": True},
}

# ---- Authentication Configuration ----
AUTH_TOKEN_KEY = "auth_token"
REFRESH_TOKEN_KEY = "refresh_token"
TOKEN_EXPIRY = 24 * 60 * 60 * 1000  # 24 hours in milliseconds
REFRESH_THRESHOLD = 5 * 60 * 1000  # 5 minutes in milliseconds

# ---- Asset Paths ----
ASSETS_DIR = Path(__file__).parent.parent / "assets"
LOGO_DIR = ASSETS_DIR / "logo"
APP_ICON = LOGO_DIR / "app-icon" / "app-icon-android.png"
FAVICON = LOGO_DIR / "favicon" / "favicon.ico"
HORIZONTAL_LOGO = LOGO_DIR / "primary" / "edgetaxai-horizontal-color.svg"
VERTICAL_LOGO = LOGO_DIR / "primary" / "edgetaxai-vertical-color.svg"
ICON_COLOR = LOGO_DIR / "icon" / "edgetaxai-icon-color.svg"

# ---- App Settings ----
APP_NAME = "TaxEdgeAI Desktop"
DEBUG_MODE = True  # Set to False for production

# ---- Logging Configuration ----
LOG_FILE = "desktop_app.log"  # Log file for desktop app
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR

# ---- IRS Configuration ----
IRS_MILEAGE_RATE = 0.655  # Default IRS mileage rate (2023)

# ---- UI Configuration ----
# Custom messages and settings for Streamlit app
WELCOME_MESSAGE = "Welcome to TaxEdgeAI - Your Tax Optimization Assistant"

# ---- Shared Feature Flags ----
ENABLE_BIOMETRIC = True
ENABLE_OFFLINE_MODE = True
ENABLE_AUTO_SYNC = True

# ---- Error Messages ----
NETWORK_ERROR_MESSAGE = "Network error occurred"
AUTHENTICATION_ERROR_MESSAGE = "Authentication failed"
VALIDATION_ERROR_MESSAGE = "Validation error"

# ---- Validation Rules ----
PASSWORD_VALIDATION_RULES = {
    "minLength": 8,
    "requireSpecialCharacter": True,
    "requireNumber": True,
}
EMAIL_VALIDATION_RULE = {"pattern": r"^[^\s@]+@[^\s@]+\.[^\s@]+$"}


def get_platform_config(platform: str) -> Dict[str, Any]:
    """Get platform-specific configuration"""
    return {
        "api_url": f"{API_CONFIG['BASE_URL']}/platforms/{platform}",
        "timeout": API_CONFIG["TIMEOUT"],
        "retry_attempts": API_CONFIG["RETRY_ATTEMPTS"],
        "sync_settings": PLATFORM_CONFIG["SYNC_SETTINGS"],
        "ui_settings": PLATFORM_CONFIG["UI_SETTINGS"],
    }
