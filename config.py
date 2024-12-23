import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables from a `.env` file
load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

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
    LOG_FILE = os.getenv("LOG_FILE", "api.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Fiverr
    FIVERR_API_KEY = os.getenv("FIVERR_API_KEY", "")

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
