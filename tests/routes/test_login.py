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


def test_login_success(client, mocker):
    """Test successful OTP generation for an existing user."""
    # Pre-populate the database with a user
    client.post("/signup", json={"phone_number": "+1234567890"})
    mocker.patch("api.routes.auth_routes.send_sms")
    # Mock SMS sending
    response = client.post("/login", json={"phone_number": "+1234567890"})
    assert response.status_code == 200
    assert b"OTP sent to your phone number" in response.data


def test_login_user_not_found(client):
    """Test login failure for a non-existing user."""
    response = client.post("/login", json={"phone_number": "+9999999999"})
    assert response.status_code == 404
    assert b"User not found." in response.data
