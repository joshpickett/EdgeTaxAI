import os
import sys
from api.setup_path import setup_python_path
from api.utils.session_manager import SessionManager
from api.utils.token_manager import TokenManager
from api.utils.rate_limit import rate_limit
from typing import Dict, Any
from http import HTTPStatus
from datetime import datetime, timedelta
from api.middleware.auth_middleware import require_auth
from api.middleware.session_middleware import validate_session
from flask import Blueprint, request, jsonify
from api.services.bank_service import BankService
from api.utils.error_handler import handle_api_error
from api.utils.audit_logger import AuditLogger
from api.utils.encryption_utils import EncryptionManager

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

# Initialize components
bank_service = BankService()
session_manager = SessionManager()
token_manager = TokenManager()
bank_routes = Blueprint("bank", __name__)
encryption_manager = EncryptionManager()
audit_logger = AuditLogger()


@bank_routes.errorhandler(Exception)
def handle_error(error):
    return handle_api_error(error)


@bank_routes.route("/link-token", methods=["POST"])
@rate_limit(max_requests=100, window_seconds=3600)
@require_auth
@validate_session()
def create_link_token() -> Dict[str, Any]:
    """Create a link token for bank integration.

    Returns:
        Dict containing the link token or error message
    """
    try:
        user_id = request.json.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id is required"}), HTTPStatus.BAD_REQUEST

        # Verify active session
        if not session_manager.validate_session(str(user_id)):
            return jsonify({"error": "Invalid session"}), HTTPStatus.UNAUTHORIZED

        audit_logger.log_bank_operation(user_id, "create_link_token", {})
        return bank_service.create_link_token(user_id), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/exchange-token", methods=["POST"])
@require_auth
@validate_session()
def exchange_public_token() -> Dict[str, Any]:
    """Exchange a public token for an access token.

    Returns:
        Dict containing the access token or error message
    """
    try:
        user_id = request.json.get("user_id")
        public_token = request.json.get("public_token")

        if not user_id or not public_token:
            return (
                jsonify({"error": "user_id and public_token are required"}),
                HTTPStatus.BAD_REQUEST,
            )

        return bank_service.exchange_public_token(user_id, public_token), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/accounts", methods=["GET"])
@require_auth
@rate_limit(max_requests=100, window_seconds=3600)
@validate_session()
def get_accounts() -> Dict[str, Any]:
    """Get user's connected bank accounts"""
    try:
        user_id = request.args.get("user_id")
        audit_logger.log_bank_operation(user_id, "get_accounts", {})
        return bank_service.get_accounts(user_id), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/transactions", methods=["GET"])
@require_auth
@rate_limit(max_requests=100, window_seconds=3600)
@validate_session()
def get_transactions() -> Dict[str, Any]:
    """Get user's transactions"""
    try:
        user_id = request.args.get("user_id")
        audit_logger.log_bank_operation(user_id, "get_transactions", {})
        return bank_service.get_transactions(user_id), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/balance", methods=["GET"])
@require_auth
@rate_limit(max_requests=100, window_seconds=3600)
@validate_session()
def get_balance() -> Dict[str, Any]:
    """Get account balances"""
    try:
        user_id = request.args.get("user_id")
        return bank_service.get_balance(user_id), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/disconnect", methods=["POST"])
@require_auth
@rate_limit(max_requests=100, window_seconds=3600)
@validate_session()
def disconnect_bank() -> Dict[str, Any]:
    """Disconnect bank integration"""
    try:
        user_id = request.json.get("user_id")
        return bank_service.disconnect_bank(user_id), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/transactions/search", methods=["POST"])
@require_auth
@validate_session()
def search_transactions() -> Dict[str, Any]:
    """Search transactions with filters"""
    try:
        user_id = request.json.get("user_id")
        filters = request.json.get("filters", {})
        return bank_service.search_transactions(user_id, filters), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/verify", methods=["GET"])
@require_auth
@rate_limit(max_requests=100, window_seconds=3600)
@validate_session()
def verify_account() -> Dict[str, Any]:
    """Verify account status"""
    try:
        user_id = request.args.get("user_id")
        return bank_service.verify_account(user_id), HTTPStatus.OK
    except Exception as e:
        raise


@bank_routes.route("/transactions/analysis", methods=["GET"])
@require_auth
@rate_limit(max_requests=100, window_seconds=3600)
@validate_session()
def analyze_transactions() -> Dict[str, Any]:
    """Analyze transaction patterns"""
    try:
        user_id = request.args.get("user_id")
        return bank_service.analyze_transactions(user_id), HTTPStatus.OK
    except Exception as e:
        raise
