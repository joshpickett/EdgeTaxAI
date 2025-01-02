import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

import sqlite3
import logging
import datetime
import random
import os
from contextlib import contextmanager, closing
from typing import Generator


class DatabaseError(Exception):
    """Custom exception for database errors"""

    pass


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection with context management"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logging.error(f"Database connection error: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Get a database cursor with context management"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            yield cursor
            conn.commit()


# Configure Logging
logging.basicConfig(
    filename="db_utils.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
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
    with Database(DATABASE_FILE).get_cursor() as cursor:
        try:
            expiry_time = datetime.datetime.now() + datetime.timedelta(
                minutes=5
            )  # OTP valid for 5 minutes
            cursor.execute(
                """
                UPDATE users 
                SET otp_code = ?, otp_expiry = ? 
                WHERE email = ? OR phone_number = ?
                """,
                (
                    otp_code,
                    expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
                    identifier,
                    identifier,
                ),
            )
            logging.info(f"OTP saved successfully for {identifier}.")
        except sqlite3.Error as e:
            logging.error(f"Error saving OTP for {identifier}: {e}")


def verify_otp_for_user(identifier, otp_code):
    """
    Verify OTP for a user identified by email or phone number.

    Args:
        identifier (str): User's email or phone number.
        otp_code (str): OTP entered by the user.

    Returns:
        True if OTP is valid, False otherwise.
    """
    with Database(DATABASE_FILE).get_cursor() as cursor:
        try:
            cursor.execute(
                """
                SELECT otp_code, otp_expiry 
                FROM users 
                WHERE (email = ? OR phone_number = ?)
                """,
                (identifier, identifier),
            )
            row = cursor.fetchone()
            if row:
                stored_otp, expiry_time = row
                if (
                    otp_code == stored_otp
                    and datetime.datetime.now()
                    <= datetime.datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S")
                ):
                    logging.info(f"OTP verified successfully for {identifier}.")
                    return True
            logging.warning(f"Invalid or expired OTP for {identifier}.")
            return False
        except sqlite3.Error as e:
            logging.error(f"Error verifying OTP for {identifier}: {e}")
            return False


def clear_otp_for_user(identifier):
    """
    Clear the OTP fields after successful verification.

    Args:
        identifier (str): User's email or phone number.
    """
    with Database(DATABASE_FILE).get_cursor() as cursor:
        try:
            cursor.execute(
                """
                UPDATE users 
                SET otp_code = NULL, otp_expiry = NULL 
                WHERE email = ? OR phone_number = ?
                """,
                (identifier, identifier),
            )
            logging.info(f"OTP cleared successfully for {identifier}.")
        except sqlite3.Error as e:
            logging.error(f"Error clearing OTP for {identifier}: {e}")


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
