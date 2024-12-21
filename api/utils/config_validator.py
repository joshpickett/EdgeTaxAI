import os
import logging
from typing import Dict, Any, Optional

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
    ]

    missing_settings = [setting for setting in required_settings 
                       if not config.get(setting)]

    if missing_settings:
        raise ConfigurationError(
            f"Missing required configuration settings: {', '.join(missing_settings)}"
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
