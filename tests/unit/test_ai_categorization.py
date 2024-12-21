import pytest


def test_add_expense_with_ai_categorization(client, mocker):
    """Test expense categorization using mocked AI response."""
    # Mock AI categorization to return 'AI-Categorized'
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="AI-Categorized")
    response = client.post("/add", json={"user_id": 1, "description": "Business Lunch", "amount": 35.0})

    # Assertions
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"AI-Categorized"' in response.data
    assert b'"description":"Business Lunch"' in response.data


def test_add_expense_empty_description(client, mocker):
    """Test that an empty description defaults to 'General'."""
    # Mock AI categorization to return 'Uncategorized'
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value="Uncategorized")
    response = client.post("/add", json={"user_id": 1, "description": "", "amount": 15.0})

    # Assertions
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"description":"General"' in response.data  # Default description
    assert b'"category":"Uncategorized"' in response.data


def test_add_expense_default_category(client, mocker):
    """Test that an expense defaults to 'General' when AI categorization fails."""
    # Mock AI categorization to fail and return None
    mocker.patch("api.routes.expense_routes.categorize_expense", return_value=None)
    response = client.post("/add", json={"user_id": 1, "description": "Miscellaneous", "amount": 10.0})

    # Assertions
    assert response.status_code == 201
    assert b"Expense added successfully" in response.data
    assert b'"category":"General"' in response.data  # Default category
    assert b'"description":"Miscellaneous"' in response.data
