import os
from dotenv import load_dotenv
from typing import Dict, Any
import json
import logging

# Load environment variables
load_dotenv()

# Configuration class
class Config:
    # API Settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Directory Settings
    SOURCE_ROOT = "api/Routes"
    TESTS_ROOT = "tests/API/Routes"
    
    # Logging Settings
    LOG_FILE = "test_generation_debug.log"
    SUMMARY_FILE = "test_summary.log"
    
    # Test Generation Settings
    TEST_FRAMEWORK = "pytest"  # or "unittest"
    MAX_RETRIES = 3
    TIMEOUT = 30
    CACHE_ENABLED = True
    CACHE_DURATION_DAYS = 7
    
    # Performance Settings
    MAX_WORKERS = 4
    BATCH_SIZE = 10
    RATE_LIMIT_DELAY = 1.0  # seconds
    
    # API Settings
    MODEL_NAME = "gpt-4"
    
    @classmethod
    def validate(cls):
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
