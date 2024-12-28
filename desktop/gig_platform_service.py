from desktop.setup_path import setup_desktop_path
setup_desktop_path()

import requests
import os
import logging
from functools import wraps
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from desktop.token_storage import TokenStorage
from desktop.config import API_CONFIG

BASE_URL = API_CONFIG['BASE_URL']
token_storage = TokenStorage(os.getenv("SECRET_KEY"))

MAX_RETRIES = 3
INITIAL_DELAY = 1  # seconds

@dataclass
class PlatformStatus:
    connected: bool
    last_sync: Optional[datetime]
    error: Optional[str] = None

class GigPlatformError(Exception):
    """Custom exception for gig platform operations"""
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def with_retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < MAX_RETRIES - 1:
                    delay = INITIAL_DELAY * (2 ** attempt)
                    logging.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s")
                    time.sleep(delay)
        raise last_exception
    return wrapper

def get_oauth_link(platform: str, redirect_uri: str) -> Optional[str]:
    """Get OAuth URL for platform connection"""
    try:
        response = requests.get(
            f"{BASE_URL}/gig/connect/{platform}",
            params={"redirect_uri": redirect_uri}
        )
        if response.status_code == 200:
            return response.json().get('oauth_url')
        logging.error(f"Failed to get OAuth URL for {platform}: {response.text}")
        return None
    except Exception as e:
        logging.error(f"Error getting OAuth URL: {e}")
        return None

@with_retry
def fetch_connected_platforms(user_id):
    """Fetch the list of connected platforms for a user"""
    try:
        response = requests.get(f"{BASE_URL}/gig/connections", params={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("connected_accounts", [])
        else:
            return []
    except Exception as e:
        logging.error(f"Error fetching connected platforms: {e}")
        return []

def fetch_platform_data(user_id, platform):
    """
    Fetch data (trips, earnings) for a connected platform.
    """
    try:
        response = requests.get(f"{BASE_URL}/gig/fetch-data", params={"user_id": user_id, "platform": platform})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data from {platform}"}
    except Exception as e:
        logging.error(f"Error fetching data from {platform}: {e}")
        return {"error": str(e)}

def refresh_platform_token(user_id: int, platform: str) -> bool:
    """Refresh access token for platform"""
    try:
        response = requests.post(
            f"{BASE_URL}/refresh-token",
            json={"user_id": user_id, "platform": platform}
        )
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Token refresh error: {e}")
        return False

def get_sync_status(user_id: int, platform: str) -> Dict[str, Any]:
    """Get platform sync status"""
    try:
        response = requests.get(
            f"{BASE_URL}/gig/sync-status",
            params={"user_id": user_id, "platform": platform}
        )
        if response.status_code == 200:
            return response.json()
        return {"status": "unknown", "last_sync": None}
    except Exception as e:
        logging.error(f"Error getting sync status: {e}")
        return {"status": "error", "error": str(e)}

def validate_platform_connection(user_id: int, platform: str) -> PlatformStatus:
    """Validate platform connection status"""
    try:
        response = requests.get(
            f"{BASE_URL}/gig/validate",
            params={"user_id": user_id, "platform": platform}
        )
        if response.status_code == 200:
            data = response.json()
            return PlatformStatus(
                connected=data.get("connected", False),
                last_sync=datetime.fromisoformat(data.get("last_sync")) if data.get("last_sync") else None
            )
        return PlatformStatus(connected=False, error="Failed to validate connection")
    except Exception as e:
        logging.error(f"Connection validation error: {e}")
        return PlatformStatus(connected=False, error=str(e))

def disconnect_platform(user_id: int, platform: str) -> bool:
    """Disconnect a gig platform"""
    try:
        response = requests.post(
            f"{BASE_URL}/gig/disconnect",
            json={"user_id": user_id, "platform": platform}
        )
        if response.status_code == 200:
            logging.info(f"Successfully disconnected {platform}")
            return True
        return False
    except Exception as e:
        logging.error(f"Error disconnecting platform: {e}")
        return False

def handle_oauth_callback(code: str, platform: str, user_id: int) -> bool:
    """Handle OAuth callback and token storage"""
    try:
        response = requests.post(f"{BASE_URL}/gig/callback", json={
            "code": code,
            "platform": platform,
            "user_id": user_id
        })
        
        if response.status_code == 200:
            token_data = response.json().get('token_data', {})
            return token_storage.store_token(user_id, platform, token_data)
        return False
    except Exception as e:
        logging.error(f"OAuth callback error: {e}")
        return False

class TokenStorage:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.platforms = {
            'uber': {
                'oauth_url': 'https://login.uber.com/oauth/v2/authorize',
                'token_url': 'https://login.uber.com/oauth/v2/token',
                'data_url': 'https://api.uber.com/v1.2/partners/trips',
                'scopes': ['partner.trips', 'partner.payments']
            },
            'lyft': {
                'oauth_url': 'https://api.lyft.com/oauth/authorize',
                'token_url': 'https://api.lyft.com/oauth/token',
                'data_url': 'https://api.lyft.com/v1/rides',
                'scopes': ['rides.read', 'offline']
            },
            'doordash': {
                'oauth_url': 'https://identity.doordash.com/connect/authorize',
                'token_url': 'https://identity.doordash.com/connect/token',
                'data_url': 'https://api.doordash.com/v1/deliveries',
                'scopes': ['delivery_status', 'earnings']
            }
        }
        self.sync_status = {}

    async def sync_platform_data(self, user_id: int, platform: str) -> bool:
        """Sync platform data with standardized approach"""
        try:
            if platform not in self.platforms:
                raise ValueError(f"Unsupported platform: {platform}")

            platform_config = self.platforms[platform]
            token = await self.get_platform_token(user_id, platform)
            
            if not token:
                raise ValueError(f"No valid token for {platform}")

            # Fetch data using platform-specific endpoint
            response = await self._fetch_platform_data(
                platform_config['data_url'],
                token,
                platform_config.get('params', {})
            )

            # Process and store data
            processed_data = await self._process_platform_data(platform, response)
            await self._store_platform_data(user_id, platform, processed_data)

            return True
        except Exception as e:
            logging.error(f"Sync error for {platform}: {e}")
            return False
