import pytest
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime
from ..routes.tax_routes import tax_bp


@pytest.fixture
def app():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(tax_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_calculator():
    with patch("api.routes.tax_routes.TaxCalculator") as mock:
        yield mock


class TestTaxRoutes:
    def test_estimate_quarterly_tax_success(self, client, mock_calculator):
        mock_calculator.return_value.calculate_quarterly_tax.return_value = {
            "quarterly_amount": 1000.00,
            "annual_tax": 4000.00,
            "effective_rate": 0.25,
        }

        response = client.post(
            "/api/tax/estimate-quarterly",
            json={"user_id": 123, "year": 2023, "quarter": 1},
        )

        assert response.status_code == 200
        data = response.json
        assert "estimate" in data
        assert "document_id" in data

    def test_real_time_tax_savings_success(self, client, mock_calculator):
        mock_calculator.return_value.calculate_tax_savings.return_value = 250.00

        response = client.post(
            "/api/tax/savings", json={"amount": 1000.00, "user_id": 123}
        )

        assert response.status_code == 200
        data = response.json
        assert "savings" in data
        assert "timestamp" in data

    def test_ai_deduction_suggestions_success(self, client):
        response = client.post(
            "/api/tax/deductions",
            json={
                "expenses": [
                    {"description": "Office supplies", "amount": 100.00},
                    {"description": "Travel expense", "amount": 500.00},
                ]
            },
        )

        assert response.status_code == 200
        assert "suggestions" in response.json

    def test_quarterly_tax_estimate_validation(self, client):
        response = client.post("/api/tax/quarterly-estimate", json={})
        assert response.status_code == 400
        assert "error" in response.json

    def test_calculate_effective_rate_success(self, client):
        response = client.post(
            "/calculate-effective-rate",
            json={"gross_income": 100000.00, "deductions": 20000.00},
        )

        assert response.status_code == 200
        data = response.json
        assert all(
            key in data
            for key in ["taxable_income", "tax_bracket", "tax_rate", "estimated_tax"]
        )

    def test_generate_tax_document_success(self, client):
        response = client.post(
            "/api/tax/document",
            json={"user_id": 123, "year": 2023, "document_type": "schedule_c"},
        )

        assert response.status_code == 200
        assert all(key in response.json for key in ["document_id", "content"])

    @patch("api.routes.tax_routes.EventSystem")
    def test_event_subscription(self, mock_event_system, client):
        mock_event_system.return_value.subscribe.assert_called_once()
        mock_event_system.return_value.publish.assert_called_once()

        response = client.post(
            "/api/tax/estimate-quarterly",
            json={"user_id": 123, "year": 2023, "quarter": 1},
        )

        assert response.status_code == 200

    def test_invalid_amount_error(self, client):
        response = client.post(
            "/api/tax/savings", json={"amount": -100, "user_id": 123}
        )

        assert response.status_code == 400
        assert "error" in response.json

    def test_document_generation_error(self, client):
        response = client.post(
            "/api/tax/document", json={"user_id": 123, "document_type": "invalid_type"}
        )

        assert response.status_code == 400
        assert "error" in response.json

    @patch("api.routes.tax_routes.get_db_connection")
    def test_database_integration(self, mock_db, client):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1000.00,)

        response = client.post(
            "/api/tax/estimate-quarterly",
            json={"user_id": 123, "year": 2023, "quarter": 1},
        )

        assert response.status_code == 200
        mock_cursor.execute.assert_called_once()

    def test_tax_bracket_calculation(self, client):
        test_cases = [
            (50000, 0.22),  # 22% bracket
            (100000, 0.24),  # 24% bracket
            (200000, 0.32),  # 32% bracket
        ]

        for income, expected_rate in test_cases:
            response = client.post(
                "/calculate-effective-rate",
                json={"gross_income": income, "deductions": 0},
            )

            assert response.status_code == 200
            assert abs(response.json["tax_rate"] - expected_rate) < 0.01
