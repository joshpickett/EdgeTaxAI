import logging
from typing import Dict, Any, Optional
import requests
from desktop.setup_path import setup_desktop_path
from shared.constants import SYNC_STATES
from desktop.utils.error_handler import handle_api_error
from desktop.config import Config

setup_desktop_path()

class SyncServiceAdapter:
    def __init__(self, base_url: str = Config.API_BASE_URL):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        self.sync_manager = SyncManager()
        self.sync_in_progress = False
        
    async def sync_data(self, user_id: str) -> Dict[str, Any]:
        """Sync all user data using shared service"""
        if self.sync_in_progress:
            return {"status": SYNC_STATES.SYNCING}
            
        try:
            # Process any pending offline operations
            await self.sync_manager.process_offline_queue()
            
            self.sync_in_progress = True
            response = requests.post(
                f"{self.base_url}/sync/data",
                json={"user_id": user_id},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as exception:
            logging.error(f"Sync error: {exception}")
            return {"status": "error", "error": str(exception)}
        finally:
            self.sync_in_progress = False
            
    async def get_sync_status(self, user_id: str) -> Dict[str, Any]:
        """Get current sync status"""
        try:
            response = requests.get(
                f"{self.base_url}/sync/status",
                params={"user_id": user_id},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as exception:
            logging.error(f"Error getting sync status: {exception}")
            return {"status": "error", "error": str(exception)}
