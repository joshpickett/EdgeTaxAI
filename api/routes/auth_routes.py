from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from ..utils.validators import validate_email, validate_phone
from ..middleware.auth_middleware import generate_token
import sqlite3
import random
import os
import re  # Added for validation

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
    expiry_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S.%f")

    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection failed")
    cursor = conn.cursor()
    cursor.execute("BEGIN TRANSACTION")
    cursor.execute(
        "UPDATE users SET otp_code = ?, otp_expiry = ? WHERE email = ? OR phone_number = ?",
        (otp_code, expiry_time, identifier, identifier),
    )
    conn.commit()
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
def signup() -> tuple[Dict[str, Any], int]:
    """
    Handles user signup with email or phone number and verifies via OTP.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get("email")
    phone_number = data.get("phone_number")

    print(f"Received email: {email}, phone_number: {phone_number}")  # Debug

    # Input Validation
    if not (email or phone_number):
        return jsonify({"error": "Email or phone number is required."}), 400

    if email and not is_valid_email(email):
        return jsonify({"error": "Invalid email format."}), 400

    if phone_number and not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number format."}), 400
    
    print("Input validation passed")

    identifier = email or phone_number

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if user already exists
        cursor.execute(
            "SELECT * FROM users WHERE email = ? OR phone_number = ?", (identifier, identifier)
        )
        if cursor.fetchone():
            return jsonify({"error": "User already exists with this email or phone number."}), 400

        logging.info(f"Creating new user with identifier: {identifier}")
        # Insert new user
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(
            "INSERT INTO users (email, phone_number, is_verified) VALUES (?, ?, 0)",
            (email, phone_number),
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Generate and send OTP
        otp_code = generate_otp()
        save_otp_for_user(identifier, otp_code)
        send_sms(phone_number, f"Your verification code is: {otp_code}")

        return jsonify({"message": "Signup successful. OTP sent for verification."}), 201
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        conn.close()


# 2. Verify OTP for Signup/Login
@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """
    Verifies the OTP entered by the user during signup or login.
    """
    data = request.json
    identifier = data.get("email") or data.get("phone_number")
    otp_code = data.get("otp_code")

    if not (identifier and otp_code):
        return jsonify({"error": "Email/Phone and OTP code are required."}), 400

    if verify_otp_for_user(identifier, otp_code):
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


# 3. OTP-Based Login
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Handles OTP-based login using email or phone number.
    """
    data = request.json
    email = data.get("email")
    phone_number = data.get("phone_number")

    # Input Validation
    if not (email or phone_number):
        return jsonify({"error": "Email or phone number is required."}), 400

    if email and not is_valid_email(email):
        return jsonify({"error": "Invalid email format."}), 400

    if phone_number and not is_valid_phone(phone_number):
        return jsonify({"error": "Invalid phone number format."}), 400

    identifier = email or phone_number

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? OR phone_number = ?", (identifier, identifier))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found."}), 404

    # Generate and send OTP
    otp_code = generate_otp()
    save_otp_for_user(identifier, otp_code)
    send_sms(user["phone_number"], f"Your login verification code is: {otp_code}")

    return jsonify({"message": "OTP sent to your phone number for login verification."}), 200
