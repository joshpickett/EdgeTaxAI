import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables from a `.env` file
load_dotenv()

# ---- General Flask Configuration ----
class Config:
    APP_NAME = "TaxEdgeAI Backend"
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"  # Enable Flask debug mode
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # Flask session encryption key

    # Test Generation Settings
    SOURCE_ROOT = "api/routes"
    TESTS_ROOT = "tests"
    TEST_FRAMEWORK = "pytest"
    CACHE_ENABLED = True
    CACHE_DURATION_DAYS = 7
    MAX_RETRIES = 3
    TIMEOUT = 30
    MODEL_NAME = "gpt-4"
    MAX_WORKERS = 4
    BATCH_SIZE = 10
    RATE_LIMIT_DELAY = 1.0

    # ---- Logging Configuration ----
    LOG_FILE = os.getenv("LOG_FILE", "api.log")  # Log file location
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()  # Logging level (DEBUG, INFO, ERROR)

    # ---- Database Configuration ----
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")  # Default SQLite database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- API Keys ----
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID", "")
    PLAID_SECRET = os.getenv("PLAID_SECRET", "")
    PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")

    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # ---- IRS Configuration ----
    IRS_MILEAGE_RATE = float(os.getenv("IRS_MILEAGE_RATE", "0.655"))  # Default IRS mileage rate

    # ---- CORS (Cross-Origin Resource Sharing) ----
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")  # Adjust for production to specific domains

    # ---- Gig Platform API Credentials ----
    # Uber
    UBER_CLIENT_ID = os.getenv("UBER_CLIENT_ID", "")
    UBER_CLIENT_SECRET = os.getenv("UBER_CLIENT_SECRET", "")
    UBER_REDIRECT_URI = os.getenv("UBER_REDIRECT_URI", "")

    # Lyft
    LYFT_CLIENT_ID = os.getenv("LYFT_CLIENT_ID", "")
    LYFT_CLIENT_SECRET = os.getenv("LYFT_CLIENT_SECRET", "")
    LYFT_REDIRECT_URI = os.getenv("LYFT_REDIRECT_URI", "")

    # DoorDash
    DOORDASH_API_KEY = os.getenv("DOORDASH_API_KEY", "")

    # Instacart
    INSTACART_API_KEY = os.getenv("INSTACART_API_KEY", "")

    # Upwork
    UPWORK_CLIENT_ID = os.getenv("UPWORK_CLIENT_ID", "")
    UPWORK_CLIENT_SECRET = os.getenv("UPWORK_CLIENT_SECRET", "")
    UPWORK_REDIRECT_URI = os.getenv("UPWORK_REDIRECT_URI", "")

    # Fiverr
    FIVERR_API_KEY = os.getenv("FIVERR_API_KEY", "")

    # Centralized configuration file for shared settings
    TAX_RATE = 0.25  # 25% tax rate

    @classmethod
    def validate(cls):
        """Validate required configuration settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        if not os.path.exists(cls.SOURCE_ROOT):
            raise ValueError(f"Source directory {cls.SOURCE_ROOT} does not exist")
            
    @classmethod
    def load_custom_config(cls, config_file: str):
        """Load custom configuration from a JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                custom_config = json.load(f)
                for key, value in custom_config.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
                    else:
                        logging.warning(f"Unknown configuration key: {key}")
