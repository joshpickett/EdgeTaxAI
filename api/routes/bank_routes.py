from flask import Blueprint, request, jsonify
import logging
import os
import datetime

# Plaid Imports
from plaid.api.plaid_api import PlaidApi
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.exceptions import ApiException

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure Logging
logging.basicConfig(
    filename="plaid_integration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Plaid Configuration
PLAID_ENVIRONMENT = os.getenv("PLAID_ENV", "sandbox")
PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
PLAID_SECRET = os.getenv("PLAID_SECRET")

# Plaid Environment Mapping
PLAID_ENVIRONMENTS = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com"
}

# Validate Plaid Environment
PLAID_HOST = PLAID_ENVIRONMENTS.get(PLAID_ENVIRONMENT, PLAID_ENVIRONMENTS["sandbox"])

configuration = Configuration(
    host=PLAID_HOST,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = ApiClient(configuration)
plaid_client = PlaidApi(api_client)

# Secure token storage (Replace with DB for production)
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
            return jsonify({"error": "User ID must be an integer."}), 400

        request_data = LinkTokenCreateRequest(
            user={"client_user_id": str(user_id)},
            client_name="TaxEdgeAI",
            products=[Products("auth"), Products("transactions")],
            country_codes=[CountryCode("US")],
            language="en"
        )
        response = plaid_client.link_token_create(request_data)
        link_token = response.link_token
        logging.info(f"Generated Plaid link token for user {user_id}")
        return jsonify({"link_token": link_token})
    except ApiException as e:
        logging.error(f"Plaid API error: {str(e)}")
        return jsonify({"error": "Failed to generate Plaid link token."}), 500

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

        request_data = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(request_data)
        access_token = response.access_token

        USER_TOKENS[user_id] = access_token

        logging.info(f"Access token stored for User ID: {user_id}")
        return jsonify({"message": "Bank account connected successfully."})
    except ApiException as e:
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
        request_data = AccountsGetRequest(access_token=access_token)
        response = plaid_client.accounts_get(request_data)

        logging.info(f"Accounts fetched for User ID: {user_id}")
        return jsonify({"accounts": response.accounts})
    except ApiException as e:
        logging.error(f"Error fetching accounts: {e}")
        return jsonify({"error": "Failed to fetch accounts."}), 500

# 4. Fetch Transactions
@bank_bp.route("/plaid/transactions", methods=["GET"])
def get_transactions():
    try:
        user_id = request.args.get("user_id", type=int)
        start_date_str = request.args.get("start_date", (datetime.date.today() - datetime.timedelta(days=30)).isoformat())
        end_date_str = request.args.get("end_date", datetime.date.today().isoformat())

        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        access_token = USER_TOKENS[user_id]
        request_data = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=10, offset=0)
        )
        response = plaid_client.transactions_get(request_data)

        logging.info(f"Transactions fetched for User ID: {user_id}")
        return jsonify({"transactions": response.transactions})
    except ValueError as ve:
        logging.error(f"Invalid date format: {ve}")
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except ApiException as e:
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
