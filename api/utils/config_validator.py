import os
import logging
from typing import Dict, Any, Optional
from .error_handler import handle_config_error

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the application configuration
    Raises ConfigurationError if required settings are missing
    """
    required_settings = [
        'SECRET_KEY',
        'DATABASE_URL',
        'PLAID_CLIENT_ID',
        'PLAID_SECRET',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'REDIS_URL',
        'SENTRY_DSN',
        'AWS_ACCESS_KEY',
        'AWS_SECRET_KEY'
    ]

    missing_settings = [setting for setting in required_settings 
                       if not config.get(setting)]

    if missing_settings:
        handle_config_error(missing_settings)

    # Validate environment-specific settings
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        prod_settings = ['SENTRY_DSN', 'AWS_ACCESS_KEY']
        missing_prod = [s for s in prod_settings if not config.get(s)]
        if missing_prod:
            handle_config_error(
                missing_prod, 
                "Production environment missing required settings"
            )

def get_database_url() -> str:
    """Get and validate database URL from environment"""
    db_url = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    if not db_url:
        raise ConfigurationError("DATABASE_URL is not configured")
    return db_url

def get_api_key(service: str) -> Optional[str]:
    """Get and validate API key for a service"""
    key = os.getenv(f'{service}_API_KEY')
    if not key:
        logging.warning(f"{service}_API_KEY is not configured")
    return key

@staticmethod
def validate_database_config(config: Dict[str, Any]) -> bool:
    """Validate database configuration settings"""
    required_database_settings = [
        'DATABASE_URL',
        'DATABASE_POOL_SIZE',
        'DATABASE_MAX_OVERFLOW'
    ]
    
    return all(
        config.get(setting) is not None 
        for setting in required_database_settings
    )

@classmethod
def load_custom_config(cls, config_file: str):
    """Load custom configuration from a JSON file"""
