import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from ..routes.reports_routes import reports_bp
from ..utils.report_generator import generate_report


@pytest.fixture
def app():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(reports_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_db():
    with patch("sqlite3.connect") as mock:
        yield mock


class TestReportsRoutes:
    def test_generate_report_success(self, client):
        response = client.post(
            "/reports/tax_summary",
            json={"type": "tax_summary", "params": {"year": 2023, "user_id": 123}},
        )
        assert response.status_code == 200
        assert isinstance(response.json, dict)

    def test_generate_tax_summary_success(self, client, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("income", 50000.00),
            ("expenses", 20000.00),
        ]

        response = client.post("/tax-summary", json={"user_id": 123, "year": 2023})

        assert response.status_code == 200
        data = response.json
        assert "income" in data
        assert "expenses" in data
        assert "net_income" in data

    def test_generate_schedule_c_success(self, client, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("office_supplies", 1000.00),
            ("travel", 2000.00),
        ]

        response = client.post("/irs/schedule-c", json={"user_id": 123, "year": 2023})

        assert response.status_code == 200
        assert "schedule_c" in response.json

    def test_generate_custom_report_success(self, client):
        response = client.post(
            "/custom-report",
            json={
                "user_id": 123,
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "categories": ["travel", "meals"],
                "report_type": "detailed",
                "format": "json",
            },
        )

        assert response.status_code == 200
        assert isinstance(response.json, dict)

    def test_generate_analytics_success(self, client, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            ("category1", 100.00, "2023-01-01"),
            ("category2", 200.00, "2023-02-01"),
        ]

        response = client.post("/analytics", json={"user_id": 123, "year": 2023})

        assert response.status_code == 200
        data = response.json
        assert "trends" in data
        assert "patterns" in data
        assert "predictions" in data

    def test_analyze_tax_savings_success(self, client):
        response = client.post("/tax-savings", json={"user_id": 123, "year": 2023})

        assert response.status_code == 200
        assert "savings" in response.json

    def test_export_report_pdf(self, client):
        response = client.post(
            "/export",
            json={"user_id": 123, "report_type": "tax_summary", "format": "pdf"},
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/pdf"

    def test_export_report_excel(self, client):
        response = client.post(
            "/export",
            json={"user_id": 123, "report_type": "tax_summary", "format": "excel"},
        )

        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["Content-Type"]

    def test_generate_advanced_analytics_success(self, client, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.execute.return_value = None
        mock_cursor.fetchall.return_value = [
            ("category1", 100.00, "2023-01-01"),
            ("category2", 200.00, "2023-02-01"),
        ]

        response = client.post(
            "/advanced-analytics", json={"user_id": 123, "year": 2023}
        )

        assert response.status_code == 200
        data = response.json
        assert "trends" in data
        assert "patterns" in data
        assert "predictions" in data
        assert "summary" in data

    def test_invalid_date_range(self, client):
        response = client.post(
            "/custom-report",
            json={
                "user_id": 123,
                "start_date": "2023-12-31",
                "end_date": "2023-01-01",  # Invalid: end before start
            },
        )

        assert response.status_code == 400
        assert "error" in response.json

    def test_missing_required_fields(self, client):
        response = client.post("/tax-summary", json={"year": 2023})  # Missing user_id

        assert response.status_code == 400
        assert "error" in response.json

    def test_invalid_report_format(self, client):
        response = client.post(
            "/export",
            json={
                "user_id": 123,
                "report_type": "tax_summary",
                "format": "invalid_format",
            },
        )

        assert response.status_code == 400
        assert "error" in response.json

    def test_trend_analysis(self, client, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("category1", 100.00, "2023-01-01"),
            ("category1", 150.00, "2023-02-01"),
            ("category1", 200.00, "2023-03-01"),
        ]

        response = client.post("/analytics", json={"user_id": 123, "year": 2023})

        assert response.status_code == 200
        data = response.json
        assert "trends" in data
        assert isinstance(data["trends"], dict)
        assert "category1" in data["trends"]
        assert "slope" in data["trends"]["category1"]

    def test_prediction_accuracy(self, client, mock_db):
        mock_cursor = Mock()
        mock_db.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("category1", 100.00, "2023-01-01"),
            ("category1", 110.00, "2023-02-01"),
            ("category1", 120.00, "2023-03-01"),
        ]

        response = client.post(
            "/advanced-analytics", json={"user_id": 123, "year": 2023}
        )

        assert response.status_code == 200
        data = response.json
        assert "predictions" in data
        assert "confidence" in data["predictions"]
        assert (
            data["predictions"]["confidence"] > 0.5
        )  # Assuming good prediction confidence

    @patch("api.utils.report_generator.analyze_expense_trends")
    def test_expense_trend_analysis(self, mock_analyze_trends, client):
        mock_analyze_trends.return_value = {
            "increasing_categories": ["category1"],
            "decreasing_categories": ["category2"],
            "stable_categories": ["category3"],
        }

        response = client.post("/analytics", json={"user_id": 123, "year": 2023})

        assert response.status_code == 200
        data = response.json
        assert "trends" in data
        assert len(data["trends"]["increasing_categories"]) > 0
