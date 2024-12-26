from flask import Blueprint, request, jsonify
from ..services.bank_service import BankService
from ..utils.error_handler import handle_api_error

# Initialize components
bank_service = BankService()
bank_routes = Blueprint('bank', __name__)

@bank_routes.route("/link-token", methods=["POST"])
def create_link_token():
    try:
        return bank_service.create_link_token(request.json.get("user_id"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bank_routes.route("/exchange-token", methods=["POST"])
def exchange_public_token():
    try:
        return bank_service.exchange_public_token(request.json.get("user_id"), request.json.get("public_token"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
