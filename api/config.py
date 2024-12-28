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
    
    # Redis Configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Default test directory structure
    TEST_BASE_DIR = "tests"
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
