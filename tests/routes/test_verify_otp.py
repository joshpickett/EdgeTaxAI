import sqlite3
from api.routes.auth_routes import save_otp_for_user, verify_otp_for_user
from datetime import datetime, timedelta

def test_verify_expired_otp():
    """Test OTP verification fails when OTP is expired."""
    identifier = "test@example.com"
    expired_time = datetime.now() - timedelta(minutes=1)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (email, otp_code, otp_expiry) VALUES (?, ?, ?)",
                   (identifier, "123456", expired_time))
    conn.commit()
    conn.close()

    result = verify_otp_for_user(identifier, "123456")
    assert not result, "Expired OTP should not be valid."
