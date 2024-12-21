import sqlite3
import logging
import datetime
import random
from twilio.rest import Client
import os

# Configure Logging
logging.basicConfig(
    filename="db_utils.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DATABASE_FILE = "database.db"

# --- Database Connection ---
def get_db_connection():
    """Establish a database connection using the DATABASE environment variable."""
    db_path = os.getenv("DATABASE", "default_database.db")
    
    # Ensure database directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir)
        except OSError as e:
            logging.error(f"Failed to create database directory: {e}")
            return None
            
    print(f"Connecting to database at: {db_path}")  # Debugging output
    return sqlite3.connect(db_path)


# --- OTP Management ---
def generate_otp():
    """
    Generate a 6-digit OTP.
    """
    return str(random.randint(100000, 999999))


def save_otp_for_user(identifier, otp_code):
    """
    Save OTP and its expiry time for a user identified by email or phone number.

    Args:
        identifier (str): User's email or phone number.
        otp_code (str): Generated OTP.
    """
    conn = get_db_connection()
    if conn is None:
        raise Exception("Database connection failed")
    cursor = conn.cursor()
    try:
        expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=5)  # OTP valid for 5 minutes
        cursor.execute(
            """
            UPDATE users 
            SET otp_code = ?, otp_expiry = ? 
            WHERE email = ? OR phone_number = ?
            """,
            (otp_code, expiry_time.strftime("%Y-%m-%d %H:%M:%S"), identifier, identifier)
        )
        conn.commit()
        logging.info(f"OTP saved successfully for {identifier}.")
    except sqlite3.Error as e:
        logging.error(f"Error saving OTP for {identifier}: {e}")
    finally:
        conn.close()


def verify_otp_for_user(identifier, otp_code):
    """
    Verify OTP for a user identified by email or phone number.

    Args:
        identifier (str): User's email or phone number.
        otp_code (str): OTP entered by the user.

    Returns:
        True if OTP is valid, False otherwise.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to verify OTP: Database connection could not be established.")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT otp_code, otp_expiry 
            FROM users 
            WHERE (email = ? OR phone_number = ?)
            """,
            (identifier, identifier)
        )
        row = cursor.fetchone()
        if row:
            stored_otp, expiry_time = row
            if otp_code == stored_otp and datetime.datetime.now() <= datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S"):
                logging.info(f"OTP verified successfully for {identifier}.")
                return True
        logging.warning(f"Invalid or expired OTP for {identifier}.")
        return False
    except sqlite3.Error as e:
        logging.error(f"Error verifying OTP for {identifier}: {e}")
        return False
    finally:
        conn.close()


def clear_otp_for_user(identifier):
    """
    Clear the OTP fields after successful verification.

    Args:
        identifier (str): User's email or phone number.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to clear OTP: Database connection could not be established.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users 
            SET otp_code = NULL, otp_expiry = NULL 
            WHERE email = ? OR phone_number = ?
            """,
            (identifier, identifier)
        )
        conn.commit()
        logging.info(f"OTP cleared successfully for {identifier}.")
    except sqlite3.Error as e:
        logging.error(f"Error clearing OTP for {identifier}: {e}")
    finally:
        conn.close()


# --- Twilio SMS Integration ---
def send_sms(phone_number, message):
    """
    Send SMS using Twilio.

    Args:
        phone_number (str): Receiver's phone number.
        message (str): SMS content.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")
    try:
        client = Client(account_sid, auth_token)
        client.messages.create(body=message, from_=from_number, to=phone_number)
        logging.info(f"SMS sent successfully to {phone_number}.")
    except Exception as e:
        logging.error(f"Failed to send SMS to {phone_number}: {e}")
        raise Exception(f"Failed to send SMS: {e}")
