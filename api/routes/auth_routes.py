# updated12262024

import os
import re
import sqlite3
import random
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta, timezone
from twilio.rest import Client
from ..utils.rate_limit import rate_limit
from ..utils.validators import validate_email, validate_phone
from ..services.auth_service import AuthService

auth_service = AuthService()

# Rate limiting constants
MAX_LOGIN_ATTEMPTS = 5
RATE_LIMIT_WINDOW = 3600  # 1 hour

# Blueprint Setup
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Utility Functions
DATABASE_FILE = os.getenv("DB_PATH", "database.db")
logging.basicConfig(level=logging.INFO)

def get_db_connection():
    """Establish a connection to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    try:
        conn.execute('SELECT 1')  # Test connection
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None
    conn.row_factory = sqlite3.Row
    return conn

def generate_otp():
    """Generate a 6-digit OTP."""
    return str(random.randint(100000, 999999))

def send_sms(phone_number, message):
    """Send SMS using Twilio."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    try:
        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_number, to=phone_number)
    except Exception as e:
        raise Exception(f"Failed to send SMS: {str(e)}")

def save_otp_for_user(identifier, otp_code):
    """Save OTP and its expiry time for a user."""
    try:
        expiry_time = (datetime.now(timezone.utc) + timedelta(minutes=5))
        
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed")
            
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE users 
               SET otp_code = ?, 
                   otp_expiry = ?,
                   otp_attempts = 0
               WHERE email = ? OR phone_number = ?""",
            (otp_code, expiry_time, identifier, identifier)
        )
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"Error saving OTP: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verify_otp_for_user(identifier, otp_code):
    """Verify OTP for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT otp_code, otp_expiry FROM users WHERE (email = ? OR phone_number = ?)",
        (identifier, identifier),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        stored_otp, expiry_time = row
        # Parse datetime with microseconds
        expiry_time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S.%f")
        if otp_code == stored_otp and datetime.now() <= expiry_time:
            return True
    return False

def is_valid_email(email):
    """Validate email format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def is_valid_phone(phone_number):
    """Validate phone number format."""
    pattern = r"^\+?[0-9]{7,15}$"  # Supports international phone numbers
    return re.match(pattern, phone_number)

# 1. OTP-Based Signup
@auth_bp.route("/signup", methods=["POST"])
@rate_limit(requests_per_minute=5)
def signup() -> tuple[Dict[str, Any], int]:
    """
    Handles user signup with email or phone number and verifies via OTP.
    """
    try:
        return auth_service.handle_signup(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Verify OTP for Signup/Login
@auth_bp.route("/verify-otp", methods=["POST"])
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
            return jsonify({"error": "Email/Phone and OTP code are required."}), 400
            
        if not otp_code or len(otp_code) != 6:
            return jsonify({"error": "Invalid OTP format"}), 400

        if auth_service.verify_otp(data):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute(
                "UPDATE users SET is_verified = 1, otp_code = NULL, otp_expiry = NULL WHERE email = ? OR phone_number = ?",
                (identifier, identifier),
            )
            conn.commit()
            logging.info(f"User verified successfully: {identifier}")
            return jsonify({"message": "OTP verified successfully! Account is active."}), 200
        return jsonify({"error": "Invalid or expired OTP."}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. OTP-Based Login
@auth_bp.route("/login", methods=["POST"])
@rate_limit(requests_per_minute=5)
def login():
    """
    Handles OTP-based login using email or phone number.
    """
    try:
        return auth_service.handle_login(request.json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/biometric/register", methods=["POST"])
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
