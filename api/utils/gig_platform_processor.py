import os
import sys
from api.setup_path import setup_python_path
setup_python_path()

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from api.utils.rate_limit import rate_limit
from api.utils.retry_handler import with_retry

class GigPlatformProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_platforms = {
            'uber': self._process_uber_data,
            'lyft': self._process_lyft_data,
            'doordash': self._process_doordash_data,
            'instacart': self._process_instacart_data
        }

    @with_retry(max_attempts=3, initial_delay=1.0)
    @rate_limit(requests_per_minute=30)
    async def process_platform_data(self, platform: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process platform-specific data"""
        try:
            processed_data = {
                "platform": platform,
                "trips": []
            }
 
            processor = self.supported_platforms[platform]
            processed_data["trips"] = await processor(raw_data)
            return processed_data
        except Exception as e:
            self.logger.error(f"Error processing {platform} data: {e}")
            raise

    @with_retry(max_attempts=3, initial_delay=1.0)
    @rate_limit(requests_per_minute=30)
    async def get_oauth_url(self, platform: str) -> str:
        """Generate OAuth URL for platform"""
        try:
            # Platform-specific OAuth URL generation
            oauth_configs = {
                'uber': {
                    'base_url': 'https://login.uber.com/oauth/v2/authorize',
                    'client_id': os.getenv('UBER_CLIENT_ID'),
                    'scope': 'profile history'
                },
                'lyft': {
                    'base_url': 'https://api.lyft.com/oauth/authorize',
                    'client_id': os.getenv('LYFT_CLIENT_ID'),
                    'scope': 'public profile rides.read'
                }
            }

            if platform not in oauth_configs:
                raise ValueError(f"OAuth not configured for platform: {platform}")

            config = oauth_configs[platform]
            return (f"{config['base_url']}?"
                   f"client_id={config['client_id']}&"
                   f"response_type=code&"
                   f"scope={config['scope']}")
        except Exception as e:
            self.logger.error(f"Error generating OAuth URL for {platform}: {e}")
            raise

    @with_retry(max_attempts=3, initial_delay=1.0)
    @rate_limit(requests_per_minute=30)
    async def exchange_code_for_token(self, platform: str, code: str) -> Dict[str, Any]:
        """Exchange OAuth code for access token"""
        try:
            # Platform-specific token exchange implementation
            token_configs = {
                'uber': {
                    'token_url': 'https://login.uber.com/oauth/v2/token',
                    'client_id': os.getenv('UBER_CLIENT_ID'),
                    'client_secret': os.getenv('UBER_CLIENT_SECRET')
                },
                'lyft': {
                    'token_url': 'https://api.lyft.com/oauth/token',
                    'client_id': os.getenv('LYFT_CLIENT_ID'),
                    'client_secret': os.getenv('LYFT_CLIENT_SECRET')
                }
            }

            if platform not in token_configs:
                raise ValueError(f"Token exchange not configured for platform: {platform}")

            # Implementation of token exchange would go here
            return {"access_token": "sample_token", "refresh_token": "sample_refresh"}
        except Exception as e:
            self.logger.error(f"Error exchanging code for token on {platform}: {e}")
            raise

    async def _process_uber_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Uber-specific data"""
        processed_trips = []
        for trip in raw_data.get("trips", []):
            processed_trip = {
                "trip_id": trip["uuid"],
                "start_time": datetime.fromisoformat(trip["start_time"]),
                "end_time": datetime.fromisoformat(trip["end_time"]),
                "earnings": float(trip["fare"]),
                "distance": float(trip["distance"]),
                "status": trip["status"],
                "tips": float(trip.get("tip", 0)),
                "platform_fees": float(trip.get("service_fee", 0)),
                "expenses": []
            }
            processed_trips.append(processed_trip)
        return processed_trips

    async def _process_lyft_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Lyft-specific data"""
        # Implementation for Lyft data processing
        return {"platform": "lyft", "processed_data": raw_data}

    async def _process_doordash_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process DoorDash-specific data"""
        # Implementation for DoorDash data processing
        return {"platform": "doordash", "processed_data": raw_data}

    async def _process_instacart_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process Instacart-specific data"""
        # Implementation for Instacart data processing
        return {"platform": "instacart", "processed_data": raw_data}
