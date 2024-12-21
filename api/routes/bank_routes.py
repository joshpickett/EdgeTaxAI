from flask import Blueprint, request, jsonify
import logging
from functools import wraps
import redis
from datetime import datetime, timedelta
from plaid.api import plaid_api
from plaid.exceptions import PlaidError
from ..utils.api_config import APIConfig
from ..utils.error_handler import handle_plaid_error
from ..utils.token_manager import TokenManager
from ..utils.monitoring import monitor_api_calls
from ..utils.cache_utils import CacheManager
from typing import Optional

# Initialize components
token_manager = TokenManager()
cache_manager = CacheManager()
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Configure Logging
logging.basicConfig(
    filename="plaid_integration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_plaid_client():
    """
    Get configured Plaid client with error handling
    """
    try:
        configuration = plaid_api.Configuration(
            host=APIConfig.get_plaid_host(),
            api_key={'clientId': APIConfig.PLAID_CLIENT_ID, 'secret': APIConfig.PLAID_SECRET}
        )
        return plaid_api.PlaidApi(plaid_api.ApiClient(configuration))
    except Exception as e:
        logging.error(f"Failed to initialize Plaid client: {e}")
        raise

# Secure token storage (Replace with Database for production)
USER_TOKENS = {}

# Placeholder AI Categorization
def categorize_transaction(description):
    return "Uncategorized"

# Rate limiting decorator
def rate_limit(max_requests=100, window=3600):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_id = request.json.get('user_id') or request.args.get('user_id')
            if not user_id:
                return jsonify({"error": "User ID required"}), 401

            rate_key = f"rate_limit:{user_id}"
            request_count = redis_client.get(rate_key)

            if request_count and int(request_count) >= max_requests:
                return jsonify({"error": "Rate limit exceeded"}), 429

            pipe = redis_client.pipeline()
            pipe.incr(rate_key)
            pipe.expire(rate_key, window)
            pipe.execute()

            return f(*args, **kwargs)
        return wrapper
    return decorator

# Blueprint for Bank Routes
bank_bp = Blueprint("banks", __name__)

def refresh_access_token(user_id: int) -> Optional[str]:
    """Refresh Plaid access token if needed."""
    try:
        if user_id not in USER_TOKENS:
            return None
            
        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.ItemGetRequest(access_token=access_token)
        plaid_client = get_plaid_client()
        
        try:
            plaid_client.item_get(request_data)
            return access_token
        except PlaidError as e:
            if e.code == "INVALID_ACCESS_TOKEN":
                # Token expired, refresh it
                refresh_request = plaid_api.ItemPublicTokenExchangeRequest(
                    public_token=get_new_public_token(user_id)
                )
                refresh_response = plaid_client.item_public_token_exchange(refresh_request)
                new_access_token = refresh_response.access_token
                
                # Update stored token
                USER_TOKENS[user_id] = new_access_token
                return new_access_token
            raise
    except Exception as e:
        logging.error(f"Error refreshing access token: {e}")
        return None

# Routes

# 1. Generate Plaid Link Token
@bank_bp.route("/plaid/link-token", methods=["POST"])
@rate_limit(max_requests=100, window=3600)
@monitor_api_calls("link_token")
def create_link_token():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid JSON payload"}), 400

        data = request.json
        user_id = data.get("user_id")
        
        if not isinstance(user_id, int):
            return jsonify({"error": "User ID must be an integer"}), 400

        request_data = plaid_api.LinkTokenCreateRequest(
            user={"client_user_id": str(user_id)},
            client_name="TaxEdgeAI",
            products=[plaid_api.Products("auth"), plaid_api.Products("transactions")],
            country_codes=[plaid_api.CountryCode("US")],
            language="en"
        )
        plaid_client = get_plaid_client()
        response = plaid_client.link_token_create(request_data)
        
        # Enhanced transaction categorization
        transactions = fetch_transactions(user_id)
        categorized_transactions = categorize_transactions(transactions)
        
        # Link with tax planning
        tax_implications = calculate_tax_implications(categorized_transactions)
        
        # Update quarterly estimates
        update_quarterly_estimates(user_id, tax_implications)
        
        # Store enhanced transaction data
        store_transaction_data(user_id, {
            'transactions': categorized_transactions,
            'tax_implications': tax_implications,
            'quarterly_estimates': quarterly_estimates
        })
        
        return jsonify({"message": "Bank data processed successfully"})
    except PlaidError as e:
        return handle_plaid_error(e)
    except Exception as e:
        logging.error(f"Plaid API error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# 2. Exchange Public Token for Access Token
@bank_bp.route("/plaid/exchange-token", methods=["POST"])
@rate_limit(max_requests=100, window=3600)
@monitor_api_calls("exchange_token")
def exchange_public_token():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid JSON payload"}), 400

        data = request.json
        user_id = data.get("user_id")
        public_token = data.get("public_token")

        if not isinstance(user_id, int) or not public_token:
            return jsonify({"error": "User ID and Public Token are required."}), 400

        request_data = plaid_api.ItemPublicTokenExchangeRequest(public_token=public_token)
        plaid_client = get_plaid_client()
        response = plaid_client.item_public_token_exchange(request_data)
        access_token = response.access_token

        USER_TOKENS[user_id] = access_token

        logging.info(f"Access token stored for User ID: {user_id}")
        return jsonify({"message": "Bank account connected successfully."})
    except Exception as e:
        logging.error(f"Error exchanging public token: {e}")
        return jsonify({"error": "Failed to exchange Plaid token."}), 500

# 3. Fetch Bank Accounts
@bank_bp.route("/plaid/accounts", methods=["GET"])
@rate_limit(max_requests=200, window=3600)
@monitor_api_calls("get_accounts")
def get_bank_accounts():
    try:
        user_id = request.args.get("user_id", type=int)

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        # Check cache
        cache_key = f"accounts:{user_id}"
        cached_response = cache_manager.get(cache_key)
        if cached_response:
            logging.info(f"Cache hit for accounts: {user_id}")
            return jsonify(cached_response)

        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.AccountsGetRequest(access_token=access_token)
        plaid_client = get_plaid_client()
        response = plaid_client.accounts_get(request_data)

        logging.info(f"Accounts fetched for User ID: {user_id}")

        # Cache the response
        cache_manager.set(cache_key, response.accounts, 300)  # Cache for 5 minutes

        return jsonify({"accounts": response.accounts})
    except Exception as e:
        logging.error(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts."}), 500

# Add Balance Check Endpoint
@bank_bp.route("/plaid/balance", methods=["GET"])
@rate_limit(max_requests=100, window=3600)
@monitor_api_calls("get_balance")
def get_account_balance():
    """Get current balance for connected accounts."""
    try:
        user_id = request.args.get("user_id", type=int)
        
        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID"}), 400
            
        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.AccountsBalanceGetRequest(access_token=access_token)
        plaid_client = get_plaid_client()
        response = plaid_client.accounts_balance_get(request_data)
        
        balances = [{
            'account_id': account.account_id,
            'balance': account.balances.current,
            'type': account.type
        } for account in response.accounts]
        
        return jsonify({"balances": balances}), 200
    except Exception as e:
        return handle_plaid_error(e)

# 4. Fetch Transactions
@bank_bp.route("/plaid/transactions", methods=["GET"])
@rate_limit(max_requests=150, window=3600)
@monitor_api_calls("get_transactions")
def get_transactions():
    try:
        user_id = request.args.get("user_id", type=int)
        start_date_str = request.args.get("start_date", (datetime.today() - timedelta(days=30)).isoformat())
        end_date_str = request.args.get("end_date", datetime.today().isoformat())

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        # Check cache
        cache_key = f"transactions:{user_id}:{start_date}:{end_date}"
        cached_response = cache_manager.get(cache_key)
        if cached_response:
            logging.info(f"Cache hit for transactions: {user_id}")
            return jsonify(cached_response)

        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=plaid_api.TransactionsGetRequestOptions(count=10, offset=0)
        )
        plaid_client = get_plaid_client()
        response = plaid_client.transactions_get(request_data)

        # Cache the response
        cache_manager.set(cache_key, {"transactions": response.transactions}, 300)

        logging.info(f"Transactions fetched for User ID: {user_id}")
        return jsonify({"transactions": response.transactions})
    except ValueError as ve:
        logging.error(f"Invalid date format: {ve}")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception as e:
        logging.error(f"Error fetching transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions."}), 500

# Add Transaction Search/Filter Endpoint
@bank_bp.route("/plaid/transactions/search", methods=["POST"])
@rate_limit(max_requests=150, window=3600)
@monitor_api_calls("search_transactions")
def search_transactions():
    """Search transactions with filters."""
    try:
        data = request.json
        user_id = data.get("user_id")
        filters = data.get("filters", {})
        
        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID"}), 400
            
        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.TransactionsGetRequest(
            access_token=access_token,
            start_date=filters.get("start_date"),
            end_date=filters.get("end_date"),
            options=plaid_api.TransactionsGetRequestOptions(
                count=filters.get("limit", 100),
                offset=filters.get("offset", 0)
            )
        )
        
        plaid_client = get_plaid_client()
        response = plaid_client.transactions_get(request_data)
        
        return jsonify({"transactions": response.transactions}), 200
    except Exception as e:
        return handle_plaid_error(e)

# 5. Disconnect Bank Account
@bank_bp.route("/plaid/disconnect", methods=["POST"])
@rate_limit(max_requests=50, window=3600)
@monitor_api_calls("disconnect_bank")
def disconnect_bank_account():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid JSON payload"}), 400

        data = request.json
        user_id = data.get("user_id")

        if not isinstance(user_id, int):
            return jsonify({"error": "Invalid or missing User ID"}), 400

        if USER_TOKENS.pop(user_id, None) is None:
            return jsonify({"error": "User ID not found"}), 404

        # Clear cached data
        cache_manager.delete(f"accounts:{user_id}")

        logging.info(f"Bank account disconnected for User ID: {user_id}")
        return jsonify({"message": "Bank account disconnected successfully."}), 200
    except Exception as e:
        logging.error(f"Error disconnecting bank account: {e}")
        return jsonify({"error": "Failed to disconnect bank account."}), 500

# Add Account Verification Status Endpoint
@bank_bp.route("/plaid/verify", methods=["GET"])
@rate_limit(max_requests=100, window=3600)
@monitor_api_calls("verify_account")
def verify_account_status():
    """Check verification status of connected accounts."""
    try:
        user_id = request.args.get("user_id", type=int)
        
        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID"}), 400
            
        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.AccountsGetRequest(access_token=access_token)
        plaid_client = get_plaid_client()
        response = plaid_client.accounts_get(request_data)
        
        verification_status = [{
            'account_id': account.account_id,
            'verified': account.verification_status == "verified",
            'status': account.verification_status
        } for account in response.accounts]
        
        return jsonify({"verification_status": verification_status}), 200
    except Exception as e:
        return handle_plaid_error(e)

# Add Historical Analysis Endpoint
@bank_bp.route("/plaid/transactions/analysis", methods=["GET"])
@rate_limit(max_requests=100, window=3600)
@monitor_api_calls("analyze_transactions")
def analyze_transactions():
    """Analyze historical transaction patterns."""
    try:
        user_id = request.args.get("user_id", type=int)
        
        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID"}), 400
            
        access_token = USER_TOKENS[user_id]
        
        # Get transactions for the last 90 days
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=90)
        
        request_data = plaid_api.TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date
        )
        
        plaid_client = get_plaid_client()
        response = plaid_client.transactions_get(request_data)
        
        # Analyze patterns
        analysis = {
            'spending_by_category': {},
            'average_transaction': sum(t.amount for t in response.transactions) / len(response.transactions),
            'largest_transaction': max(t.amount for t in response.transactions),
            'most_frequent_merchant': max(
                set(t.merchant_name for t in response.transactions if t.merchant_name),
                key=lambda x: sum(1 for t in response.transactions if t.merchant_name == x)
            )
        }
        
        return jsonify({"analysis": analysis}), 200
    except Exception as e:
        return handle_plaid_error(e)

def categorize_transactions(transactions):
    """Enhanced transaction categorization with AI"""
    categorized = []
    for transaction in transactions:
        category = ai_categorize_transaction(transaction)
        recurring = detect_recurring_pattern(transaction)
        tax_category = map_to_tax_category(category)
        
        categorized.append({
            **transaction,
            'category': category,
            'is_recurring': recurring,
            'tax_category': tax_category
        })
    return categorized

def detect_recurring_pattern(transaction):
    """Detect recurring transaction patterns"""
    # Implementation for recurring detection
    return {
        'is_recurring': False,
        'frequency': None,
        'confidence': 0.0
    }
