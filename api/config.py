import os
from dotenv import load_dotenv
import json
import logging
from typing import Dict, Any

# Load environment variables from a `.env` file
load_dotenv()

# Shared configuration constants
SHARED_CONFIG = {
    'API_VERSION': 'v1',
    'DEFAULT_TIMEOUT': 30000,
    'RETRY_ATTEMPTS': 3,
    'CACHE_DURATION': 3600,
    'PLATFORMS': ['uber', 'lyft', 'doordash', 'instacart']
}

# ---- General Flask Configuration ----
class Config:
    APP_NAME = "TaxEdgeAI Backend"
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"  # Enable Flask debug mode
    
    # OCR Configuration
    OCR_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    OCR_ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    OCR_UPLOAD_FOLDER = "uploads"
    OCR_RATE_LIMIT = {
        'DEFAULT': 100,  # requests per minute
        'BATCH': 50     # requests per minute for batch operations
    }
    
    # IRS Quarterly Tax Due Dates
    QUARTERLY_TAX_DATES = {
        1: {'start': '-01-01', 'end': '-03-31', 'due': '-04-15'},  # Q1
        2: {'start': '-04-01', 'end': '-06-30', 'due': '-06-15'},  # Q2
        3: {'start': '-07-01', 'end': '-09-30', 'due': '-09-15'},  # Q3
        4: {'start': '-10-01', 'end': '-12-31', 'due': '-01-15'}   # Q4 (due next year)
    }

    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Test Generation Settings
    # Source directories to process (with their corresponding test directories)
    TEST_MAPPING = {
        "source_dirs": [
            "api/models",
            "api/middleware",
            "api/routes",
            "api/utils"
        ],
        "test_base_dir": "tests"
    }
    
    # Default test directory structure
    TEST_BASE_DIR = "tests"
    DEFAULT_TEST_TYPE = "unit"  # Options: unit, integration, end-to-end
    TEST_FRAMEWORK = "pytest"
    CACHE_ENABLED = True
    CACHE_DURATION_DAYS = 0  # Set to 0 to disable caching
    MAX_RETRIES = 3
    TOKENS_PER_MINUTE = 10000
    BATCH_SIZE = 5  # Process 5 files at a time
    MAX_WORKERS = 4  # Maximum concurrent workers
    RATE_LIMIT_DELAY = 1.0  # Delay between batches in seconds
    MODEL_NAME = "gpt-4"  # Specify the OpenAI model to use
    TIMEOUT = 30
    SUMMARY_FILE = "test_summary.txt"

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

    # Shared Platform Settings
    PLATFORM_SETTINGS = {
        'SYNC_INTERVAL': int(os.getenv('SYNC_INTERVAL', '3600')),
        'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '100')),
        'CACHE_ENABLED': os.getenv('CACHE_ENABLED', 'True').lower() == 'true',
        'ERROR_RETRY_ATTEMPTS': int(os.getenv('ERROR_RETRY_ATTEMPTS', '3')),
        'AUTO_SYNC_ENABLED': os.getenv('AUTO_SYNC_ENABLED', 'True').lower() == 'true'
    }

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
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")  # Base URL for API
    AUTH_TOKEN_KEY = 'auth_token'  # Key for authentication token
    REFRESH_TOKEN_KEY = 'refresh_token'  # Key for refresh token
    TOKEN_EXPIRY = 86400000  # 24 hours in milliseconds
    REFRESH_THRESHOLD = 300000  # 5 minutes in milliseconds

    @classmethod
    def validate(cls):
        """Validate required configuration settings."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        if not os.path.exists(cls.TEST_MAPPING):
            raise ValueError(f"Source directory {cls.TEST_MAPPING} does not exist")
            
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

    @classmethod
    def get_platform_config(cls, platform: str) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        platform_config = {
            'api_base_url': cls.API_BASE_URL,
            'timeout': cls.PLATFORM_SETTINGS['DEFAULT_TIMEOUT'],
            'retry_attempts': cls.PLATFORM_SETTINGS['ERROR_RETRY_ATTEMPTS'],
            'batch_size': cls.PLATFORM_SETTINGS['BATCH_SIZE'],
            'sync_interval': cls.PLATFORM_SETTINGS['SYNC_INTERVAL'],
            'cache_enabled': cls.PLATFORM_SETTINGS['CACHE_ENABLED']
        }
        return platform_config
