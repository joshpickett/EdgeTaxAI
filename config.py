# config.py - Streamlit Desktop Configuration

# ---- API Configuration ----
# Base URL for the Flask backend API
API_BASE_URL = "http://localhost:5000/api"  # Update this for production/staging

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
