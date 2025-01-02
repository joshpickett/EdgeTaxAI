import sys
import os
import pytest
from flask import Flask
from api.routes.auth_routes import auth_bp


# Add the 'api/models' directory to the Python module search path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models"))
)


@pytest.fixture
def client():
    """Flask test client setup."""
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config["TESTING"] = True
    return app.test_client()


def test_signup_invalid_email(client):
    """Test signup with an invalid email format."""
    response = client.post("/signup", json={"email": "invalid-email"})
    assert response.status_code == 400
    assert b"Invalid email format" in response.data


def test_signup_invalid_phone(client):
    """Test signup with an invalid phone number format."""
    response = client.post("/signup", json={"phone_number": "12345"})
    assert response.status_code == 400
    assert b"Invalid phone number format" in response.data


def test_signup_no_input(client):
    """Test signup with no email or phone number."""
    response = client.post("/signup", json={})
    assert response.status_code == 400
    assert b"Email or phone number is required" in response.data
