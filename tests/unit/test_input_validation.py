import pytest
from flask import Flask
from api.routes.expense_routes import expense_bp


@pytest.fixture
def client():
    """Flask test client for expense routes."""
    app = Flask(__name__)
    app.register_blueprint(expense_bp)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


# ---------------- Test Cases ---------------- #

# Test missing required fields
def test_add_expense_missing_fields(client):
    """Test adding an expense with missing required fields."""

    # Missing user_id (should return 400 Bad Request)
    response = client.post("/add", json={"description": "Groceries", "amount": 50.0})
    assert response.status_code == 400
    assert b"Invalid user ID" in response.data

    # Missing description (defaults to 'General')
    response = client.post("/add", json={"user_id": 1, "amount": 50.0})
    assert response.status_code == 201  # Success
    assert b"Expense added successfully" in response.data
    assert b'"description":"General"' in response.data
    assert b'"category":"General"' in response.data

    # Missing amount (should return 400 Bad Request)
    response = client.post("/add", json={"user_id": 1, "description": "Groceries"})
    assert response.status_code == 400
    assert b"Amount must be a positive number" in response.data


# Test valid data with and without description
def test_add_expense_valid_data(client, mocker):
    """Test adding an expense with valid data."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="General")

    # Valid expense with description
    response = client.post("/add", json={"user_id": 1, "description": "Lunch", "amount": 15.0})
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"Lunch"' in response.data

    # Valid expense without description (defaults to 'General')
    response = client.post("/add", json={"user_id": 1, "amount": 20.0})
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"General"' in response.data


# Test default category when AI categorization fails
def test_add_expense_default_category(client, mocker):
    """Test that an expense defaults to 'General' when AI categorization fails."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value=None)

    # Valid expense with description
    response = client.post("/add", json={"user_id": 1, "description": "Miscellaneous", "amount": 20.0})
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"Miscellaneous"' in response.data


# Test explicitly empty description
def test_add_expense_empty_description(client, mocker):
    """Test adding an expense with an explicitly empty description."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="General")

    response = client.post("/add", json={"user_id": 1, "description": "", "amount": 10.0})
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"General"' in response.data

import pytest
from flask import Flask
from api.routes.bank_routes import bank_bp

@pytest.fixture
def client():
    """Flask test client for bank routes."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

def test_fetch_transactions_missing_fields(client):
    """Test that required fields are validated properly."""
    # Missing access_token
    response = client.post("/fetch-transactions", json={
        "account_id": "account_123",
        "start_date": "2024-12-01",
        "end_date": "2024-12-19"
    })
    assert response.status_code == 400
    assert b"Missing access token" in response.data

    # Missing account_id
    response = client.post("/fetch-transactions", json={
        "access_token": "valid_token",
        "start_date": "2024-12-01",
        "end_date": "2024-12-19"
    })
    assert response.status_code == 400
    assert b"Missing account ID" in response.data

import pytest
from flask import Flask
from api.routes.bank_routes import bank_bp

@pytest.fixture
def client():
    """Flask test client for bank routes."""
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_validate_input_missing_fields(client):
    """Test input validation for missing required fields."""
    response = client.post("/transactions", json={"account_id": ""})
    assert response.status_code == 400
    assert b"Account ID is required" in response.data

def test_validate_invalid_data(client):
    """Test input validation for invalid data."""
    response = client.post("/transactions", json={"account_id": "12345", "invalid_key": "test"})
    assert response.status_code == 400
    assert b"Invalid input data" in response.data
