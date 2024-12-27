import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional
from utils.api_config import APIConfig
from utils.cache_utils import CacheManager
from utils.analytics_helper import AnalyticsHelper
from utils.analytics_integration import AnalyticsIntegration
from datetime import datetime, timedelta
import logging

class BankService:
    def __init__(self):
        self.cache_manager = CacheManager()
        self.analytics_helper = AnalyticsHelper()
        self.analytics_integration = AnalyticsIntegration()
        self.user_tokens = {}
        
    def get_plaid_client(self):
        """Get configured Plaid client"""
        try:
            configuration = plaid_api.Configuration(
                host=APIConfig.get_plaid_host(),
                api_key={
                    'clientId': APIConfig.PLAID_CLIENT_ID,
                    'secret': APIConfig.PLAID_SECRET
                }
            )
            return plaid_api.PlaidApi(plaid_api.ApiClient(configuration))
        except Exception as e:
            logging.error(f"Plaid client initialization error: {e}")
            raise
            
    def create_link_token(self, user_id: int) -> tuple[Dict[str, Any], int]:
        """Create Plaid link token"""
        try:
            request_data = plaid_api.LinkTokenCreateRequest(
                user={"client_user_id": str(user_id)},
                client_name="TaxEdgeAI",
                products=[plaid_api.Products("auth"), plaid_api.Products("transactions")],
                country_codes=[plaid_api.CountryCode("US")],
                language="en"
            )
            
            client = self.get_plaid_client()
            response = client.link_token_create(request_data)
            
            return {"link_token": response.link_token}, 200
            
        except Exception as e:
            logging.error(f"Link token creation error: {e}")
            return {"error": str(e)}, 500
            
    def exchange_public_token(self, user_id: int, public_token: str) -> tuple[Dict[str, Any], int]:
        """Exchange public token for access token"""
        try:
            client = self.get_plaid_client()
            request_data = plaid_api.ItemPublicTokenExchangeRequest(
                public_token=public_token
            )
            
            response = client.item_public_token_exchange(request_data)
            self.user_tokens[user_id] = response.access_token
            
            return {"message": "Bank account connected successfully."}, 200
            
        except Exception as e:
            logging.error(f"Token exchange error: {e}")
            return {"error": str(e)}, 500
            
    def get_transactions(self, user_id: int, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> tuple[Dict[str, Any], int]:
        """Get user's transactions"""
        try:
            if user_id not in self.user_tokens:
                return {"error": "No connected bank account."}, 400
                
            # Check cache
            cache_key = f"transactions:{user_id}:{start_date}:{end_date}"
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data, 200
                
            client = self.get_plaid_client()
            request_data = plaid_api.TransactionsGetRequest(
                access_token=self.user_tokens[user_id],
                start_date=start_date or (datetime.now() - timedelta(days=30)).date(),
                end_date=end_date or datetime.now().date()
            )
            
            response = client.transactions_get(request_data)
            
            # Cache response
            self.cache_manager.set(cache_key, {"transactions": response.transactions}, 300)
            
            return {"transactions": response.transactions}, 200
            
        except Exception as e:
            logging.error(f"Transaction fetch error: {e}")
            return {"error": str(e)}, 500
