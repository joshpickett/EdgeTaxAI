import os
import sys
from api.setup_path import setup_python_path
from api.utils.ai_utils import AITransactionAnalyzer
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from api.models.bank_accounts import BankAccounts
from api.models.expenses import Expenses
from api.models.income import Income
from api.models.bank_transaction import BankTransaction
from api.models.tax_payments import TaxPayments
from api.schemas.bank_schemas import bank_account_schema, bank_accounts_schema
from utils.api_config import APIConfig
from utils.cache_utils import CacheManager
from utils.analytics_helper import AnalyticsHelper
from utils.analytics_integration import AnalyticsIntegration
from utils.bank_audit_logger import BankAuditLogger
from utils.encryption_utils import EncryptionManager
from utils.rate_limit import RateLimiter
from utils.monitoring import MonitoringSystem
from datetime import datetime, timedelta
import logging
from decimal import Decimal

class BankService:
    def __init__(self, db: Session):
        self.db = db
        self.monitoring = MonitoringSystem()
        self.ai_analyzer = AITransactionAnalyzer()
        self.audit_logger = BankAuditLogger(db)
        self.encryption_manager = EncryptionManager()
        self.rate_limiter = RateLimiter()
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
            
            exchange_response = client.item_public_token_exchange(request_data)
            
            # Get accounts associated with this item
            accounts_response = client.accounts_get({
                "access_token": exchange_response.access_token
            })
            
            # Store each account in the database
            stored_accounts = []
            for account in accounts_response.accounts:
                bank_account = BankAccounts(
                    user_id=user_id,
                    plaid_access_token=exchange_response.access_token,
                    plaid_item_id=exchange_response.item_id,
                    plaid_account_id=account.account_id,
                    plaid_institution_id=account.institution_id,
                    account_name=account.name,
                    official_name=account.official_name,
                    account_mask=account.mask,
                    account_type=account.type,
                    account_subtype=account.subtype
                )
                self.db.add(bank_account)
                stored_accounts.append(bank_account)
            
            self.db.commit()
            
            # Start initial transaction sync
            self._sync_transactions(user_id, exchange_response.access_token)

            # Log the successful exchange
            self.audit_logger.log_connection_attempt(
                user_id=user_id,
                bank_name="plaid",
                status="success"
            )

            return {"message": "Bank account connected successfully."}, 200
            
        except Exception as e:
            logging.error(f"Token exchange error: {e}")
            return {"error": str(e)}, 500
            
    def get_transactions(self, user_id: int, start_date: Optional[str] = None, 
                        end_date: Optional[str] = None) -> tuple[Dict[str, Any], int]:
        """Get user's transactions"""
        try:
            # Rate limiting check
            if not self.rate_limiter.check_rate(f"transactions:{user_id}"):
                return {"error": "Rate limit exceeded"}, 429

            # Monitor request
            self.monitoring.log_performance_metric(
                "transaction_fetch",
                start_time=datetime.now()
            )
            
            transactions = self._fetch_transactions(user_id)
            self.audit_logger.log_transaction_sync(
                user_id=user_id,
                transaction_count=len(transactions)
            )
            
            return {"transactions": transactions}, 200
            
        except Exception as e:
            logging.error(f"Transaction fetch error: {e}")
            return {"error": str(e)}, 500

    def _fetch_transactions(self, user_id: int) -> List[Dict[str, Any]]:
        """Fetch and process transactions"""
        try:
            transactions = self._get_raw_transactions(user_id)
            processed_transactions = []
            
            for transaction in transactions:
                # Use AI to analyze transaction
                analysis = self.ai_analyzer.analyze_transaction(transaction)
                
                if analysis.get('is_business_expense'):
                    # Save as business expense
                    expense = Expenses(
                        user_id=user_id,
                        amount=transaction['amount'],
                        description=transaction['description'],
                        category=analysis['category'],
                        date=transaction['date']
                    )
                    self.db.add(expense)
                
                elif analysis.get('is_business_income'):
                    # Save as business income
                    income = Income(
                        user_id=user_id,
                        platform_name='bank_transfer',
                        gross_income=transaction['amount'],
                        payer_name=transaction.get('merchant_name', 'Unknown'),
                        total_compensation=transaction['amount']
                    )
                    self.db.add(income)
                
                processed_transactions.append({**transaction, **analysis})
            
            self.db.commit()
            return processed_transactions

    def get_accounts(self, user_id: int) -> tuple[Dict[str, Any], int]:
        """Get user's connected bank accounts"""
        try:
            if user_id not in self.user_tokens:
                return {"error": "No connected bank account."}, 400
                
            client = self.get_plaid_client()
            response = client.accounts_get({
                "access_token": self.user_tokens[user_id]
            })
            
            return {"accounts": response.accounts}, 200
            
        except Exception as e:
            logging.error(f"Account fetch error: {e}")
            return {"error": str(e)}, 500

    def get_balance(self, user_id: int) -> tuple[Dict[str, Any], int]:
        """Get account balances"""
        try:
            if user_id not in self.user_tokens:
                return {"error": "No connected bank account."}, 400
                
            client = self.get_plaid_client()
            response = client.accounts_balance_get({
                "access_token": self.user_tokens[user_id]
            })
            
            balances = [{
                "account_id": account.account_id,
                "balance": account.balances.current
            } for account in response.accounts]
            
            return {"balances": balances}, 200
            
        except Exception as e:
            logging.error(f"Balance fetch error: {e}")
            return {"error": str(e)}, 500

    def disconnect_bank(self, user_id: int) -> tuple[Dict[str, Any], int]:
        """Disconnect bank integration"""
        try:
            if user_id not in self.user_tokens:
                return {"error": "No connected bank account."}, 400
                
            # Remove access token
            self.user_tokens.pop(user_id)
            return {"message": "Bank account disconnected successfully."}, 200
            
        except Exception as e:
            logging.error(f"Disconnect error: {e}")
            return {"error": str(e)}, 500

    def search_transactions(self, user_id: int, filters: Dict) -> tuple[Dict[str, Any], int]:
        """Search transactions with filters"""
        try:
            transactions_response = self.get_transactions(user_id)
            if "error" in transactions_response[0]:
                return transactions_response
                
            transactions = transactions_response[0]["transactions"]
            filtered_transactions = self.analytics_helper.filter_transactions(
                transactions, filters
            )
            
            return {"transactions": filtered_transactions}, 200
            
        except Exception as e:
            logging.error(f"Transaction search error: {e}")
            return {"error": str(e)}, 500

    def verify_account(self, user_id: int) -> tuple[Dict[str, Any], int]:
        """Verify account status"""
        try:
            accounts_response = self.get_accounts(user_id)
            if "error" in accounts_response[0]:
                return accounts_response
                
            verification_status = "verified" if accounts_response[0]["accounts"] else "unverified"
            return {"verification_status": verification_status}, 200
            
        except Exception as e:
            logging.error(f"Verification error: {e}")
            return {"error": str(e)}, 500

    def analyze_transactions(self, user_id: int) -> tuple[Dict[str, Any], int]:
        """Analyze transaction patterns"""
        try:
            transactions_response = self.get_transactions(user_id)
            if "error" in transactions_response[0]:
                return transactions_response
                
            transactions = transactions_response[0]["transactions"]
            analysis = self.analytics_integration.analyze_spending_patterns(transactions)
            
            return {"analysis": analysis}, 200
            
        except Exception as e:
            logging.error(f"Analysis error: {e}")
            return {"error": str(e)}, 500

    def _sync_transactions(self, user_id: int, access_token: str) -> None:
        """Sync transactions for a given access token"""
        try:
            client = self.get_plaid_client()
            
            # Get transactions for the last 30 days
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = datetime.now().strftime('%Y-%m-%d')
            
            request = plaid_api.TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date,
                end_date=end_date
            )
            
            response = client.transactions_get(request)
            transactions = response.transactions
            
            # Store transactions in database
            for transaction in transactions:
                bank_account = self.db.query(BankAccounts).filter(
                    BankAccounts.plaid_account_id == transaction.account_id,
                    BankAccounts.user_id == user_id
                ).first()
                
                if bank_account:
                    new_transaction = BankTransaction(
                        bank_account_id=bank_account.id,
                        plaid_transaction_id=transaction.transaction_id,
                        amount=transaction.amount,
                        date=transaction.date,
                        description=transaction.name,
                        merchant_name=transaction.merchant_name,
                        categories=transaction.category,
                        pending=transaction.pending
                    )
                    self.db.add(new_transaction)
            
            self.db.commit()
            
            # Update last sync time
            self.db.query(BankAccounts).filter(
                BankAccounts.plaid_access_token == access_token
            ).update({
                "last_sync": datetime.now()
            })
            self.db.commit()
            
        except Exception as e:
            logging.error(f"Error syncing transactions: {e}")
            raise

    async def initiate_ach_payment(
        self,
        user_id: int,
        bank_account_id: str,
        amount: Decimal,
        payment_type: str
    ) -> Dict[str, Any]:
        """Initiate ACH payment"""
        try:
            # Verify bank account
            bank_account = self.db.query(BankAccounts).filter(
                BankAccounts.id == bank_account_id,
                BankAccounts.user_id == user_id,
                BankAccounts.is_active == True
            ).first()
            
            if not bank_account:
                raise ValueError("Invalid bank account")

            # Create ACH payment record
            payment = TaxPayments(
                user_id=user_id,
                bank_account_id=bank_account_id,
                amount=amount,
                payment_type=payment_type,
                status='pending'
            )
            
            self.db.add(payment)
            self.db.commit()
            
            return {"payment_id": payment.id, "status": "pending"}
            
        except Exception as e:
            logging.error(f"ACH payment error: {e}")
            raise
