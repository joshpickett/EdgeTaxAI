from flask import Blueprint, request, jsonify
from utils.db_utils import get_db_connection
from utils.auth_utils import hash_password, verify_password
import sqlite3
import logging

# Configure Logging
logging.basicConfig(
    filename="auth_routes.log",  # Log file for authentication routes
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint setup
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    User Signup Endpoint: Registers a new user with full name, email, phone number, and password.
    """
    data = request.json
    full_name = data.get("full_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    password = data.get("password")

    if not all([full_name, email, phone_number, password]):
        return jsonify({"error": "All fields are required."}), 400

    conn = get_db_connection()
    if not conn:
        logging.error("Database connection could not be established during signup.")
        return jsonify({"error": "Internal server error. Please try again later."}), 500

    try:
        cursor = conn.cursor()
        # Check for duplicate email or phone number
        cursor.execute(
            "SELECT * FROM users WHERE email = ? OR phone_number = ?", (email, phone_number)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            logging.warning(f"Signup attempt failed: Duplicate email or phone ({email}, {phone_number}).")
            return jsonify({"error": "A user with this email or phone number already exists."}), 409

        # Hash the password
        hashed_password = hash_password(password)

        # Insert the new user
        cursor.execute(
            "INSERT INTO users (full_name, email, phone_number, password) VALUES (?, ?, ?, ?)",
            (full_name, email, phone_number, hashed_password)
        )
        conn.commit()
        logging.info(f"New user created successfully: {email}")
        return jsonify({"message": "Account created successfully. Please log in."}), 201

    except sqlite3.Error as e:
        logging.exception(f"Database error during signup: {e}")
        return jsonify({"error": "Failed to create account. Please try again later."}), 500
    finally:
        conn.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User Login Endpoint: Authenticates a user with email/phone and password.
    """
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not all([email, password]):
        return jsonify({"error": "Email and password are required."}), 400

    conn = get_db_connection()
    if not conn:
        logging.error("Database connection could not be established during login.")
        return jsonify({"error": "Internal server error. Please try again later."}), 500

    try:
        cursor = conn.cursor()
        # Fetch user by email or phone
        cursor.execute("SELECT * FROM users WHERE email = ? OR phone_number = ?", (email, email))
        user = cursor.fetchone()

        if user and verify_password(password, user["password"]):
            logging.info(f"User login successful: {email}")
            return jsonify({"message": "Login successful.", "user_id": user["id"]}), 200
        else:
            logging.warning(f"Login attempt failed: Invalid credentials for {email}")
            return jsonify({"error": "Invalid email or password."}), 401

    except sqlite3.Error as e:
        logging.exception(f"Database error during login: {e}")
        return jsonify({"error": "Failed to log in. Please try again later."}), 500
    finally:
        conn.close()
