from flask import Blueprint, request, jsonify
import plaid
import os
import logging
import datetime

# Configure Logging
logging.basicConfig(
    filename="plaid_integration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Plaid Client
plaid_client = plaid.Client(
    client_id=os.getenv("PLAID_CLIENT_ID"),
    secret=os.getenv("PLAID_SECRET"),
    environment="sandbox"  # Change to "development" or "production" when ready
)

# Blueprint for Bank Routes
bank_bp = Blueprint("banks", __name__)

# In-memory store (Replace with a database in production)
USER_TOKENS = {}

# 1. Generate Plaid Link Token
@bank_bp.route("/plaid/link-token", methods=["POST"])
def create_link_token():
    """
    Generate a Plaid Link Token for initializing Plaid Link.
    """
    try:
        data = request.json
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "User ID is required."}), 400

        response = plaid_client.LinkToken.create({
            "user": {"client_user_id": str(user_id)},
            "client_name": "TaxEdgeAI",
            "products": ["auth", "transactions"],
            "country_codes": ["US"],
            "language": "en"
        })

        logging.info(f"Link token generated for User ID: {user_id}")
        return jsonify({"link_token": response["link_token"]})
    except Exception as e:
        logging.error(f"Error generating Plaid link token: {str(e)}")
        return jsonify({"error": "Failed to generate Plaid link token."}), 500


# 2. Exchange Public Token for Access Token
@bank_bp.route("/plaid/exchange-token", methods=["POST"])
def exchange_public_token():
    """
    Exchange Plaid Public Token for an Access Token.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        public_token = data.get("public_token")

        if not user_id or not public_token:
            return jsonify({"error": "User ID and Public Token are required."}), 400

        response = plaid_client.Item.public_token.exchange(public_token)
        access_token = response["access_token"]

        # Store the access token (Replace this with a database for production)
        USER_TOKENS[user_id] = access_token

        logging.info(f"Access token stored for User ID: {user_id}")
        return jsonify({"message": "Bank account connected successfully."})
    except Exception as e:
        logging.error(f"Error exchanging public token: {str(e)}")
        return jsonify({"error": "Failed to exchange Plaid token."}), 500


# 3. Fetch Bank Accounts
@bank_bp.route("/plaid/accounts", methods=["GET"])
def get_bank_accounts():
    """
    Fetch all bank accounts linked to the user.
    """
    try:
        user_id = request.args.get("user_id")

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        access_token = USER_TOKENS[user_id]
        response = plaid_client.Accounts.get(access_token)

        logging.info(f"Accounts fetched for User ID: {user_id}")
        return jsonify({"accounts": response["accounts"]})
    except Exception as e:
        logging.error(f"Error fetching accounts: {str(e)}")
        return jsonify({"error": "Failed to fetch accounts."}), 500


# 4. Fetch Transactions
@bank_bp.route("/plaid/transactions", methods=["GET"])
def get_transactions():
    """
    Fetch transactions for the linked bank accounts.
    """
    try:
        user_id = request.args.get("user_id")
        start_date = request.args.get("start_date", (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = request.args.get("end_date", datetime.datetime.now().strftime("%Y-%m-%d"))

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        access_token = USER_TOKENS[user_id]
        response = plaid_client.Transactions.get(access_token, start_date, end_date)

        logging.info(f"Transactions fetched for User ID: {user_id}")
        return jsonify({"transactions": response["transactions"]})
    except Exception as e:
        logging.error(f"Error fetching transactions: {str(e)}")
        return jsonify({"error": "Failed to fetch transactions."}), 500


# 5. Disconnect Bank Account
@bank_bp.route("/plaid/disconnect", methods=["POST"])
def disconnect_bank_account():
    """
    Disconnect a bank account linked via Plaid.
    """
    try:
        data = request.json
        user_id = data.get("user_id")

        if not user_id or user_id not in USER_TOKENS:
            return jsonify({"error": "Invalid or missing User ID."}), 400

        access_token = USER_TOKENS.pop(user_id, None)  # Remove access token
        if access_token:
            logging.info(f"Bank account disconnected for User ID: {user_id}")
            return jsonify({"message": "Bank account disconnected successfully."})
        else:
            return jsonify({"error": "Bank account not found."}), 404
    except Exception as e:
        logging.error(f"Error disconnecting bank account: {str(e)}")
        return jsonify({"error": "Failed to disconnect bank account."}), 500
