import pytest
from flask import Flask
from ...routes.tax_routes import tax_bp
from unittest.mock import patch, MagicMock
from decimal import Decimal


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(tax_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_estimate_quarterly_tax(client):
    """Test quarterly tax estimation endpoint"""
    with patch("api.routes.tax_routes.calculator") as mock_calc:
        mock_calc.calculate_quarterly_tax.return_value = {
            "quarterly_amount": 1250.00,
            "annual_tax": 5000.00,
            "effective_rate": 0.25,
        }

        response = client.post(
            "/api/tax/quarterly-estimate",
            json={
                "user_id": 1,
                "quarter": 1,
                "year": 2023,
                "income": 5000.00,
                "expenses": 1000.00,
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["quarterly_tax"] == 1250.00
        assert data["annual_tax"] == 5000.00


def test_calculate_effective_rate(client):
    """Test effective tax rate calculation"""
    response = client.post(
        "/calculate-effective-rate",
        json={"gross_income": 50000.00, "deductions": 10000.00},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "tax_rate" in data
    assert "estimated_tax" in data
    assert "taxable_income" in data


def test_generate_tax_document(client):
    """Test tax document generation"""
    with patch("api.routes.tax_routes.document_manager") as mock_doc:
        mock_doc.store_document.return_value = "doc123"

        response = client.post(
            "/api/tax/document",
            json={"user_id": 1, "year": 2023, "document_type": "schedule_c"},
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "document_id" in data


def test_real_time_tax_savings(client):
    """Test real-time tax savings calculation"""
    response = client.post("/api/tax/savings", json={"amount": 1000.00, "user_id": 1})

    assert response.status_code == 200
    data = response.get_json()
    assert "savings" in data
    assert "timestamp" in data


def test_ai_deduction_suggestions(client):
    """Test AI-powered deduction suggestions"""
    response = client.post(
        "/api/tax/deductions",
        json={
            "expenses": [
                {"description": "Gas", "amount": 50.00},
                {"description": "Office supplies", "amount": 100.00},
            ]
        },
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "suggestions" in data
