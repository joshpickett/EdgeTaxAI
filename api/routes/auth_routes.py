import sys
import os
import logging
from ..setup_path import setup_python_path
setup_python_path(__file__)

from flask import Blueprint, request, jsonify
from ..services.auth_service import AuthService
from ..services.db_service import DatabaseService
from ..utils.otp_manager import OTPManager
from ..utils.token_storage import TokenStorage
from ..utils.rate_limit import rate_limit
from ..exceptions.auth_exceptions import AuthenticationError

db_service = DatabaseService()
auth_service = AuthService()
auth_blueprint = Blueprint("auth", __name__, url_prefix="/api/auth")

# Utility Functions
DATABASE_FILE = os.getenv("DB_PATH", "database.db")

# 1. OTP-Based Signup
@auth_blueprint.route("/signup", methods=["POST"])
@rate_limit(requests_per_minute=5)
def signup():
    """Handle user signup with email or phone number verification."""
    try:
        return jsonify({"message": "OTP sent for verification"}), 201
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logging.error(f"Signup error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# 2. Verify OTP for Signup/Login
@auth_blueprint.route("/verify-otp", methods=["POST"])
@rate_limit(requests_per_minute=3)
def verify_otp():
    """
    Verifies the OTP entered by the user during signup or login.
    """
    try:
        data = request.json
        identifier = data.get("email") or data.get("phone_number")
        otp_code = data.get("otp_code")

        if not identifier:
            return jsonify({"error": "Email/Phone and OTP code are required"}), 400
            
        if not otp_code or len(otp_code) != 6:
            return jsonify({"error": "Invalid OTP format"}), 400

        if auth_service.verify_otp(data):
            conn = db_service.get_connection()
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute(
                "UPDATE users SET is_verified = 1, otp_code = NULL, otp_expiry = NULL WHERE email = ? OR phone_number = ?",
                (identifier, identifier),
            )
            conn.commit()
            logging.info(f"User verified successfully: {identifier}")
            return jsonify({"message": "OTP verified successfully"}), 200
        return jsonify({"error": "Invalid or expired OTP."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. OTP-Based Login
@auth_blueprint.route("/login", methods=["POST"])
@rate_limit(requests_per_minute=5)
def login():
    """
    Handles OTP-based login using email or phone number.
    """
    try:
        if not check_login_attempts(request.remote_addr):
            return jsonify({"error": "Too many login attempts"}), 429
            
        data = request.json
        identifier = data.get("email") or data.get("phone_number")
        
        # Check if user exists first
        if not identifier or not auth_service.user_exists(identifier):
            return jsonify({"error": "User not found"}), 404
            
        return auth_service.handle_login(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_blueprint.route("/biometric/register", methods=["POST"])
def register_biometric():
    """Register biometric data for mobile authentication"""
    try:
        data = request.json
        user_id = data.get('user_id')
        biometric_data = data.get('biometric_data')
        
        if not all([user_id, biometric_data]):
            return jsonify({"error": "Missing required data"}), 400
            
        success = auth_service.handle_biometric_registration(user_id, biometric_data)
        if success:
            return jsonify({
                "message": "Biometric authentication registered successfully"
            }), 200
        return jsonify({"error": "Failed to register biometric data"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(auth_blueprint)
    app.run(debug=True)
