from typing import Dict, Any, Optional
import requests
import logging
from desktop.utils.error_handler import handle_api_error
from desktop.config import Config
from desktop.setup_path import setup_desktop_path

setup_desktop_path()

class AIServiceAdapter:
    """Adapter for shared AI service functionality"""
    
    def __init__(self, base_url: str = Config.API_BASE_URL):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
    
    async def categorize_expense(self, description: str, amount: float) -> Dict[str, Any]:
        """Categorize expense using shared AI service"""
        try:
            response = requests.post(
                f"{self.base_url}/ai/categorize",
                json={"description": description, "amount": amount},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error categorizing expense: {e}")
            return {"category": "other", "confidence": 0.0}
    
    async def analyze_receipt(self, receipt_text: str) -> Optional[Dict[str, Any]]:
        """Analyze receipt using shared AI service"""
        try:
            response = requests.post(
                f"{self.base_url}/ai/analyze-receipt",
                json={"text": receipt_text},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error analyzing receipt: {e}")
            return None
