import pytest
import requests
from datetime import datetime, timedelta


def test_expense_workflow():
    """Test complete expense addition workflow"""
    # Create expense
    expense_data = {
        "description": "Test Expense",
        "amount": 100.00,
        "category": "Office",
    }

    response = requests.post("http://localhost:5000/api/expenses", json=expense_data)
    assert response.status_code == 201
    expense_id = response.json()["id"]

    # Verify expense exists
    response = requests.get(f"http://localhost:5000/api/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json()["amount"] == 100.00

    # Update expense
    update_data = {"amount": 150.00}
    response = requests.put(
        f"http://localhost:5000/api/expenses/{expense_id}", json=update_data
    )
    assert response.status_code == 200

    # Delete expense
    response = requests.delete(f"http://localhost:5000/api/expenses/{expense_id}")
    assert response.status_code == 200


def test_tax_optimization_workflow():
    """Test tax optimization integration"""
    # Add sample expenses
    expenses = [
        {"description": "Office Rent", "amount": 1000.00, "category": "Office"},
        {"description": "Gas", "amount": 50.00, "category": "Vehicle"},
    ]

    expense_ids = []
    for expense in expenses:
        response = requests.post("http://localhost:5000/api/expenses", json=expense)
        assert response.status_code == 201
        expense_ids.append(response.json()["id"])

    # Get tax optimization suggestions
    response = requests.get(
        "http://localhost:5000/api/tax-optimization",
        params={"expense_ids": expense_ids},
    )
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert len(suggestions) > 0


def test_report_generation():
    """Test report generation workflow"""
    # Add test data
    expense_data = {
        "description": "Test Expense",
        "amount": 100.00,
        "category": "Office",
    }

    response = requests.post("http://localhost:5000/api/expenses", json=expense_data)
    assert response.status_code == 201

    # Generate report
    response = requests.get(
        "http://localhost:5000/api/reports/generate",
        params={
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat(),
        },
    )
    assert response.status_code == 200
    assert "report_url" in response.json()


def test_user_authentication_flow():
    """Test user authentication flow"""
    # User login
    login_data = {"username": "testuser", "password": "testpassword"}
    response = requests.post("http://localhost:5000/api/auth/login", json=login_data)
    assert response.status_code == 200
    assert "token" in response.json()


def test_bank_integration_workflow():
    """Test bank integration workflow"""
    # Simulate bank account linking
    bank_data = {"account_number": "123456789", "routing_number": "987654321"}
    response = requests.post("http://localhost:5000/api/bank/link", json=bank_data)
    assert response.status_code == 200
    assert response.json()["status"] == "linked"


def test_gig_platform_connection_flow():
    """Test gig platform connection flow"""
    # Simulate connecting to a gig platform
    gig_data = {"platform": "GigPlatform", "api_key": "testapikey"}
    response = requests.post("http://localhost:5000/api/gig/connect", json=gig_data)
    assert response.status_code == 200
    assert response.json()["status"] == "connected"


def test_mileage_tracking_integration():
    """Test mileage tracking integration"""
    # Simulate mileage tracking
    mileage_data = {"miles": 100, "date": "2023-10-01"}
    response = requests.post(
        "http://localhost:5000/api/mileage/track", json=mileage_data
    )
    assert response.status_code == 200
    assert response.json()["status"] == "tracked"
