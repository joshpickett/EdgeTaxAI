import sys
import os
import sqlite3
from datetime import datetime, timedelta
from api.routes.auth_routes import save_otp_for_user, get_db_connection

# Add the 'api/models' directory to the Python module search path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models"))
)


def test_save_otp_for_user():
    """Test that OTP and expiry are correctly saved in the database."""
    identifier = "+1234567890"
    otp_code = "123456"
    expiry_time = datetime.now() + timedelta(minutes=5)

    # Initialize database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        phone_number TEXT,
        otp_code TEXT,
        otp_expiry TEXT,
        is_verified INTEGER DEFAULT 0
    )
"""
    )

    cursor.execute("INSERT INTO users (phone_number) VALUES (?)", (identifier,))
    conn.commit()

    # Save OTP
    save_otp_for_user(identifier, otp_code)

    # Validate OTP and expiry in the database
    cursor.execute(
        "SELECT otp_code, otp_expiry FROM users WHERE phone_number = ?", (identifier,)
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None, "User record not found."
    assert row[0] == otp_code, "OTP code was not saved correctly."
    assert (
        datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f") > datetime.now()
    ), "OTP expiry time is invalid."
