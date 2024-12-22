# config.py - Streamlit Desktop Configuration

from pathlib import Path

# ---- API Configuration ----
# Base URL for the Flask backend API
API_BASE_URL = "http://localhost:5000/api"  # Update this for production/staging

# ---- Asset Paths ----
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
LOGO_DIR = ASSETS_DIR / 'logo'
APP_ICON = LOGO_DIR / 'app-icon' / 'app-icon-android.png'
FAVICON = LOGO_DIR / 'favicon' / 'favicon.ico'
HORIZONTAL_LOGO = LOGO_DIR / 'primary' / 'edgetaxai-horizontal-color.svg'
VERTICAL_LOGO = LOGO_DIR / 'primary' / 'edgetaxai-vertical-color.svg'
ICON_COLOR = LOGO_DIR / 'icon' / 'edgetaxai-icon-color.svg'

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
