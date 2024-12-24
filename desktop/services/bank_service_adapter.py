from typing import Dict, Any, Optional
import requests
import logging
from ..utils.error_handler import handle_api_error
from ..config import Config

class BankServiceAdapter:
    """Adapter for shared bank service functionality"""
    
    def __init__(self, base_url: str = Config.API_BASE_URL):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
    
    async def get_link_token(self, user_id: str) -> Optional[str]:
        """Get Plaid link token"""
        try:
            response = requests.post(
                f"{self.base_url}/banks/plaid/link-token",
                json={"user_id": user_id},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json().get('link_token')
        except Exception as e:
            logging.error(f"Error getting link token: {e}")
            return None
    
    async def exchange_token(self, public_token: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Exchange public token for access token"""
        try:
            response = requests.post(
                f"{self.base_url}/banks/plaid/exchange-token",
                json={"public_token": public_token, "user_id": user_id},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error exchanging token: {e}")
            return None
