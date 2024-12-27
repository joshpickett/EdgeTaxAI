import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional, List
from utils.gig_platform_processor import GigPlatformProcessor
from utils.gig_utils import PlatformAPI
from models.gig_data import GigData
from ..models.gig_model import init_gig_table
from utils.cache_utils import CacheManager
from datetime import datetime
import logging

class GigPlatformService:
    def __init__(self):
        self.processor = GigPlatformProcessor()
        self.gig_data = GigData()
        self.cache = CacheManager()
        init_gig_table()

    def connect_platform(self, platform: str, user_id: int) -> Dict[str, Any]:
        """Handle platform connection process"""
        try:
            oauth_url = self.processor.get_oauth_url(platform)
            if not oauth_url:
                return {"error": f"Failed to generate OAuth URL for {platform}"}, 400

            # Store connection attempt in database
            self.gig_data.update_sync_status(
                user_id=user_id,
                platform=platform,
                status="connecting"
            )

            return {"oauth_url": oauth_url}, 200
        except Exception as e:
            logging.error(f"Platform connection error: {e}")
            return {"error": str(e)}, 500

    async def handle_oauth_callback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process OAuth callback and store platform tokens"""
        try:
            user_id = data.get("user_id")
            platform = data.get("platform")
            code = data.get("code")

            if not all([user_id, platform, code]):
                return {"error": "Missing required fields"}, 400

            # Exchange code for tokens
            token_data = await self.processor.exchange_code_for_token(platform, code)
            
            # Store platform data
            self.gig_data.store_platform_data(user_id, platform, token_data)

            # Initialize platform sync
            await self.sync_platform_data(user_id, platform)

            return {"message": "Platform connected successfully"}, 200
        except Exception as e:
            logging.error(f"OAuth callback error: {e}")
            return {"error": str(e)}, 500

    async def sync_platform_data(self, user_id: int, platform: str) -> Dict[str, Any]:
        """Sync data from connected platform"""
        try:
            # Get platform API client
            api_client = PlatformAPI(platform, self._get_access_token(user_id, platform))

            # Fetch and process platform data
            raw_data = await api_client.fetch_trips()
            processed_data = await self.processor.process_platform_data(platform, raw_data)

            # Store processed data
            self.gig_data.store_trip(processed_data)

            # Update sync status
            self.gig_data.update_sync_status(
                user_id=user_id,
                platform=platform,
                status="success"
            )

            return processed_data, 200
        except Exception as e:
            logging.error(f"Platform sync error: {e}")
            self.gig_data.update_sync_status(
                user_id=user_id,
                platform=platform,
                status="failed",
                error=str(e)
            )
            return {"error": str(e)}, 500

    def get_platform_earnings(self, user_id: int, platform: str, 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get earnings data from platform"""
        try:
            # Check cache first
            cache_key = f"earnings:{user_id}:{platform}:{start_date}:{end_date}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data, 200

            # Fetch fresh data
            api_client = PlatformAPI(platform, self._get_access_token(user_id, platform))
            earnings_data = api_client.fetch_earnings(start_date, end_date)

            # Cache the results
            self.cache.set(cache_key, earnings_data, 3600)  # Cache for 1 hour

            return earnings_data, 200
        except Exception as e:
            logging.error(f"Error fetching earnings: {e}")
            return {"error": str(e)}, 500

    def _get_access_token(self, user_id: int, platform: str) -> str:
        """Get platform access token from database"""
        # Implementation would fetch token from database
        pass
