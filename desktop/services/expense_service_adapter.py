from typing import Dict, Any, Optional
import requests
import logging
from desktop.setup_path import setup_desktop_path
from shared.constants import PLATFORMS, EXPENSE_CATEGORIES, TAX_CATEGORIES
from desktop.config import Config
from desktop.utils.error_handler import handle_api_error

setup_desktop_path()


class ExpenseServiceAdapter:
    def __init__(self, base_url: str = Config.API_BASE_URL):
        self.base_url = base_url

    def create_expense(self, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(f"{self.base_url}/expenses", json=expense_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error creating expense: {e}")
            return None

    async def sync_platform_data(self, platform: str) -> bool:
        """Sync platform data using shared service"""
        try:
            if platform not in PLATFORMS.values():
                raise ValueError(f"Invalid platform: {platform}")

            response = requests.post(
                f"{self.base_url}/platforms/sync/{platform}", headers=self.headers
            )

            if response.status_code == 200:
                return True
            return False

        except Exception as e:
            logging.error(f"Platform sync error: {e}")
            return False
