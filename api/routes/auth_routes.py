import logging
import os
from flask import Blueprint, request, jsonify
from api.setup_path import setup_python_path
from api.services.auth_service import AuthService
from api.services.db_service import DatabaseService
from api.utils.token_manager import TokenManager
from api.utils.session_manager import SessionManager
from api.utils.rate_limit import rate_limit
from api.exceptions.auth_exceptions import AuthenticationError

setup_python_path(__file__)

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
        data = request.json
        if not data.get("email") and not data.get("phone_number"):
            return jsonify({"error": "Email or phone number required"}), 400

        # Apply rate limiting
        if not check_login_attempts(request.remote_addr):
            return jsonify({"error": "Too many attempts. Please try again later"}), 429

        response = auth_service.handle_signup(data)
        return jsonify(response[0]), response[1]
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
        if auth_service.verify_otp(data):
            user = auth_service.get_user_by_identifier(
                data.get("email") or data.get("phone_number")
            )
            if not user:
                return jsonify({"error": "User not found"}), 404

            auth_service.update_last_login(user.id)
            # Generate tokens after successful verification
            access_token = TokenManager.generate_access_token(data)
            refresh_token = TokenManager.generate_refresh_token(data)
            # Create session
            SessionManager.create_session(data, request.headers.get("User-Agent"))
            return (
                jsonify(
                    {
                        "message": "OTP verified successfully",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }
                ),
                200,
            )

        identifier = data.get("email") or data.get("phone_number")
        otp_code = data.get("otp_code")

        if not identifier:
            return jsonify({"error": "Email/Phone and OTP code are required"}), 400

        if not otp_code or len(otp_code) != 6:
            return jsonify({"error": "Invalid OTP format"}), 400

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
        data = request.json
        response = auth_service.handle_login(data)
        if response.get("success"):
            # Generate tokens
            access_token = TokenManager.generate_access_token(data)
            refresh_token = TokenManager.generate_refresh_token(data)
            # Create session
            SessionManager.create_session(data, request.headers.get("User-Agent"))
            return (
                jsonify(
                    {
                        "message": "Login successful",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }
                ),
                200,
            )

        return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_blueprint.route("/biometric/register", methods=["POST"])
@rate_limit(requests_per_minute=3)
def register_biometric():
    """Register biometric data for mobile authentication"""
    try:
        data = request.json
        user_id = data.get("user_id")
        biometric_data = data.get("biometric_data")

        if not all([user_id, biometric_data]):
            return jsonify({"error": "Missing required data"}), 400

        success = auth_service.handle_biometric_registration(user_id, biometric_data)
        if success:
            return (
                jsonify(
                    {"message": "Biometric authentication registered successfully"}
                ),
                200,
            )
        return jsonify({"error": "Failed to register biometric data"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_blueprint.route("/biometric/verify", methods=["POST"])
def verify_biometric():
    """Verify biometric data for authentication"""
    try:
        data = request.json
        user_id = data.get("user_id")
        biometric_data = data.get("biometric_data")

        if not all([user_id, biometric_data]):
            return jsonify({"error": "Missing required data"}), 400

        if auth_service.verify_biometric(user_id, biometric_data):
            auth_service.update_last_login(user_id)
            return jsonify({"message": "Biometric verification successful"}), 200
        return jsonify({"error": "Biometric verification failed"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(auth_blueprint)
    app.run(debug=True)
