import os
import sys
from api.setup_path import setup_python_path

setup_python_path()

from typing import Dict, Any, Optional
import aiohttp
import logging
from datetime import datetime
from api.utils.rate_limit import rate_limit
from api.utils.retry_handler import with_retry


class PlatformAPI:
    def __init__(self, platform: str, access_token: str):
        self.platform = platform
        self.access_token = access_token
        self.logger = logging.getLogger(__name__)
        self.base_urls = {
            "uber": "https://api.uber.com/v1",
            "lyft": "https://api.lyft.com/v1",
            "doordash": "https://api.doordash.com/v1",
            "instacart": "https://api.instacart.com/v1",
        }

    @with_retry(max_attempts=3, initial_delay=1.0)
    @rate_limit(requests_per_minute=30)
    async def fetch_trips(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch trip data from platform API"""
        try:
            if self.platform not in self.base_urls:
                raise ValueError(f"Unsupported platform: {self.platform}")

            base_url = self.base_urls[self.platform]
            endpoint = f"{base_url}/trips"

            params = {"start_date": start_date, "end_date": end_date}

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, params=params, headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(
                            f"API request failed with status {response.status}"
                        )
        except Exception as e:
            self.logger.error(f"Error fetching trips from {self.platform}: {e}")
            raise

    @with_retry(max_attempts=3, initial_delay=1.0)
    @rate_limit(requests_per_minute=30)
    async def fetch_earnings(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch earnings data from platform API"""
        try:
            if self.platform not in self.base_urls:
                raise ValueError(f"Unsupported platform: {self.platform}")

            base_url = self.base_urls[self.platform]
            endpoint = f"{base_url}/earnings"

            params = {"start_date": start_date, "end_date": end_date}

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint, params=params, headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(
                            f"API request failed with status {response.status}"
                        )
        except Exception as e:
            self.logger.error(f"Error fetching earnings from {self.platform}: {e}")
            raise

    @with_retry(max_attempts=3, initial_delay=1.0)
    @rate_limit(requests_per_minute=30)
    async def update_status(self, trip_id: str, status: str) -> Dict[str, Any]:
        """Update trip status"""
        try:
            if self.platform not in self.base_urls:
                raise ValueError(f"Unsupported platform: {self.platform}")

            base_url = self.base_urls[self.platform]
            endpoint = f"{base_url}/trips/{trip_id}/status"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            data = {"status": status}

            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    endpoint, json=data, headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(
                            f"API request failed with status {response.status}"
                        )
        except Exception as e:
            self.logger.error(f"Error updating status on {self.platform}: {e}")
            raise
