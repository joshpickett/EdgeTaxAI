import sys
import os
import pytest
import sqlite3
from flask import Flask
from api.routes.auth_routes import auth_bp

# Add the 'api/models' directory to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models")))

@pytest.fixture
def client():
    """Flask test client setup with a fresh database."""
    # Flask app setup
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config["TESTING"] = True

    # Database setup: Recreate the 'users' table
    db_path = "database.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            phone_number TEXT,
            otp_code TEXT,
            otp_expiry TEXT,
            is_verified INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

    # Return test client
    return app.test_client()

def test_signup_success(client, mocker):
    """Test successful user signup and OTP generation."""
    # Mock SMS sending to avoid external calls
    mocker.patch("api.routes.auth_routes.send_sms")
    response = client.post("/signup", json={"phone_number": "+1234567890"})
    assert response.status_code == 201
    assert b"Signup successful. OTP sent for verification." in response.data

def test_signup_user_exists(client):
    """Test signup failure when the user already exists."""
    # First signup
    client.post("/signup", json={"phone_number": "+1234567890"})

    # Second signup with the same phone number
    response = client.post("/signup", json={"phone_number": "+1234567890"})
    assert response.status_code == 400
    assert b"User already exists" in response.data
