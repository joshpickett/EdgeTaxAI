import pytest
from flask import Flask
from api.routes.expense_routes import expense_bp

# ---------------- Test Setup ---------------- #
@pytest.fixture
def client():
    """Flask test client for the expense routes."""
    app = Flask(__name__)
    app.register_blueprint(expense_bp)
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

# ---------------- Test Cases ---------------- #

# 1. Successful expense addition
def test_add_expense_success(client, mocker):
    """Test adding an expense successfully."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="Food")
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Lunch at a restaurant",
        "amount": 20.0
    })
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"Food"' in response.data

# 2. Missing fields: user_id and description
def test_add_expense_missing_fields(client):
    """Test adding an expense with missing required fields."""
    # Missing user_id
    response = client.post("/add", json={"description": "Groceries", "amount": 50.0})
    assert response.status_code == 400
    assert b"Invalid user ID" in response.data

    # Missing description (defaults to 'General')
    response = client.post("/add", json={"user_id": 1, "amount": 50.0})
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"General"' in response.data

# 3. Empty description explicitly provided
def test_add_expense_empty_description(client, mocker):
    """Test adding an expense with an explicitly empty description."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="General")
    response = client.post("/add", json={
        "user_id": 1,
        "description": "",
        "amount": 10.0
    })
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"General"' in response.data

# 4. Negative amount value
def test_add_expense_negative_amount(client):
    """Test adding an expense with a negative amount."""
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Dinner",
        "amount": -10.0
    })
    assert response.status_code == 400
    assert b"Amount must be a positive number" in response.data

# 5. Zero amount value
def test_add_expense_zero_amount(client):
    """Test adding an expense with a zero amount."""
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Dinner",
        "amount": 0.0
    })
    assert response.status_code == 400
    assert b"Amount must be a positive number" in response.data

# 6. Default category when AI categorization fails
def test_add_expense_default_category(client, mocker):
    """Test that the expense defaults to 'General' when AI categorization fails."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value=None)
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Miscellaneous",
        "amount": 20.0
    })
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"Miscellaneous"' in response.data

# 7. Valid data with AI categorization failure fallback
def test_add_expense_valid_data_with_fallback(client, mocker):
    """Test adding an expense with valid data when AI categorization fails."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="General")
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Utilities",
        "amount": 60.0
    })
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
    assert b'"description":"Utilities"' in response.data

# 8. Missing amount field
def test_add_expense_missing_amount(client):
    """Test adding an expense without providing the amount."""
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Dinner"
    })
    assert response.status_code == 400
    assert b"Amount must be a positive number" in response.data

# 9. Invalid user_id type
def test_add_expense_invalid_user_id(client):
    """Test adding an expense with an invalid user_id type."""
    response = client.post("/add", json={
        "user_id": "invalid_id",
        "description": "Dinner",
        "amount": 20.0
    })
    assert response.status_code == 400
    assert b"Invalid user ID" in response.data

# 10. AI categorization fallback to rule-based logic
def test_add_expense_ai_fallback_to_rule_based(client, mocker):
    """Test fallback to rule-based categorization when AI fails."""
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="General")
    response = client.post("/add", json={
        "user_id": 1,
        "description": "Groceries",
        "amount": 35.0
    })
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data
