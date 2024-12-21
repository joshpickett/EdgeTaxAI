from flask import Blueprint, request, jsonify
import logging
from plaid.api import plaid_api
from plaid.exceptions import PlaidError
from ..utils.api_config import APIConfig
from ..utils.error_handler import handle_plaid_error
from datetime import datetime

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

# Blueprint for Bank Routes
bank_bp = Blueprint("banks", __name__)

# Routes

# 1. Generate Plaid Link Token
@bank_bp.route("/plaid/link-token", methods=["POST"])
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
        return jsonify({"link_token": response.link_token})
    except PlaidError as e:
        return handle_plaid_error(e)
    except Exception as e:
        logging.error(f"Plaid API error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# 2. Exchange Public Token for Access Token
@bank_bp.route("/plaid/exchange-token", methods=["POST"])
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
def get_bank_accounts():
    try:
        user_id = request.args.get("user_id", type=int)

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.AccountsGetRequest(access_token=access_token)
        plaid_client = get_plaid_client()
        response = plaid_client.accounts_get(request_data)

        logging.info(f"Accounts fetched for User ID: {user_id}")
        return jsonify({"accounts": response.accounts})
    except Exception as e:
        logging.error(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts."}), 500

# 4. Fetch Transactions
@bank_bp.route("/plaid/transactions", methods=["GET"])
def get_transactions():
    try:
        user_id = request.args.get("user_id", type=int)
        start_date_str = request.args.get("start_date", (datetime.today() - timedelta(days=30)).isoformat())
        end_date_str = request.args.get("end_date", datetime.today().isoformat())

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        access_token = USER_TOKENS[user_id]
        request_data = plaid_api.TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=plaid_api.TransactionsGetRequestOptions(count=10, offset=0)
        )
        plaid_client = get_plaid_client()
        response = plaid_client.transactions_get(request_data)

        logging.info(f"Transactions fetched for User ID: {user_id}")
        return jsonify({"transactions": response.transactions})
    except ValueError as ve:
        logging.error(f"Invalid date format: {ve}")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception as e:
        logging.error(f"Error fetching transactions: {e}")
        return jsonify({"error": "Failed to fetch transactions."}), 500

# 5. Disconnect Bank Account
@bank_bp.route("/plaid/disconnect", methods=["POST"])
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

        logging.info(f"Bank account disconnected for User ID: {user_id}")
        return jsonify({"message": "Bank account disconnected successfully."}), 200
    except Exception as e:
        logging.error(f"Error disconnecting bank account: {e}")
        return jsonify({"error": "Failed to disconnect bank account."}), 500
