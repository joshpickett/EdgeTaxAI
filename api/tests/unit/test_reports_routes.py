import pytest
from flask import Flask
from ...routes.reports_routes import reports_bp
from unittest.mock import patch, MagicMock
import io


@pytest.fixture
def app():
    """Create test Flask application"""
    app = Flask(__name__)
    app.register_blueprint(reports_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_generate_tax_summary(client):
    """Test generating tax summary"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator:
        mock_generator.generate_tax_summary.return_value = {
            "total_income": 50000,
            "total_expenses": 15000,
            "net_income": 35000,
            "estimated_tax": 7000,
        }

        response = client.post(
            "/reports/tax-summary", json={"user_id": 1, "year": 2023}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["total_income"] == 50000
        assert data["estimated_tax"] == 7000


def test_generate_quarterly_summary(client):
    """Test generating quarterly summary"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator, patch(
        "api.routes.reports_routes.tax_calculator"
    ) as mock_calculator:

        mock_generator.generate_quarterly_report.return_value = {
            "income": 15000,
            "expenses": 5000,
        }

        mock_calculator.calculate_quarterly_tax.return_value = {
            "amount": 2000,
            "rate": 0.25,
        }

        response = client.post(
            "/reports/quarterly-tax", json={"user_id": 1, "year": 2023, "quarter": 1}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "tax_estimates" in data
        assert data["income"] == 15000


def test_generate_custom_report(client):
    """Test generating custom report"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator:
        mock_generator.generate_custom_report.return_value = {
            "data": [
                {"category": "gas", "amount": 100},
                {"category": "meals", "amount": 50},
            ],
            "total": 150,
        }

        response = client.post(
            "/custom-report",
            json={
                "user_id": 1,
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "categories": ["gas", "meals"],
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert len(data["data"]) == 2
        assert data["total"] == 150


def test_generate_analytics(client):
    """Test generating analytics"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator:
        mock_generator.generate_analytics.return_value = {
            "trends": {
                "monthly": {"Jan": 1000, "Feb": 1200},
                "categories": {"gas": 500, "meals": 300},
            }
        }

        response = client.post("/analytics", json={"user_id": 1, "year": 2023})

        assert response.status_code == 200
        data = response.get_json()
        assert "trends" in data
        assert "monthly" in data["trends"]


def test_analyze_tax_savings(client):
    """Test analyzing tax savings"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator:
        mock_generator.analyze_tax_savings.return_value = {
            "potential_savings": 2000,
            "recommendations": ["Consider tracking mileage", "Keep meal receipts"],
        }

        response = client.post("/tax-savings", json={"user_id": 1, "year": 2023})

        assert response.status_code == 200
        data = response.get_json()
        assert data["potential_savings"] == 2000
        assert len(data["recommendations"]) == 2


def test_export_report_pdf(client):
    """Test exporting report as PDF"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator:
        mock_generator.generate_report.return_value = {"data": "test report data"}

        response = client.post(
            "/export",
            json={"user_id": 1, "report_type": "tax_summary", "format": "pdf"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"


def test_export_report_excel(client):
    """Test exporting report as Excel"""
    with patch("api.routes.reports_routes.report_generator") as mock_generator:
        mock_generator.generate_report.return_value = {"data": "test report data"}

        response = client.post(
            "/export",
            json={"user_id": 1, "report_type": "tax_summary", "format": "excel"},
        )

        assert response.status_code == 200
        assert (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in response.headers["Content-Type"]
        )
