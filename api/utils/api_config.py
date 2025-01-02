import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    filename="api_config.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class APIConfig:
    PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    PLAID_SECRET = os.getenv("PLAID_SECRET")
    PLAID_ENV = os.getenv("PLAID_ENV", "sandbox")
    PLAID_ENDPOINTS = {
        "sandbox": "https://sandbox.plaid.com",
        "development": "https://development.plaid.com",
        "production": "https://api.plaid.com",
    }

    @classmethod
    def get_plaid_host(cls):
        """Get Plaid API host based on environment."""
        try:
            host = cls.PLAID_ENDPOINTS.get(
                cls.PLAID_ENV, cls.PLAID_ENDPOINTS["sandbox"]
            )
            logging.info(f"Using Plaid host: {host}")
            return host
        except Exception as e:
            logging.error(f"Error getting Plaid host: {e}")
            return cls.PLAID_ENDPOINTS["sandbox"]
