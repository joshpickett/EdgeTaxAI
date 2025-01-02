import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from ..routes.mileage_routes import mileage_bp


@pytest.fixture
def app():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(mileage_bp)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_google_api():
    with patch("requests.get") as mock:
        yield mock


class TestMileageRoutes:
    def test_calculate_mileage_success(self, client, mock_google_api):
        mock_google_api.return_value.json.return_value = {
            "status": "OK",
            "routes": [{"legs": [{"distance": {"text": "10.5 mi"}}]}],
        }

        response = client.post(
            "/mileage",
            json={
                "start": "123 Start St",
                "end": "456 End Ave",
                "purpose": "Client Meeting",
                "recurring": False,
            },
        )

        assert response.status_code == 200
        assert "distance" in response.json
        assert "tax_deduction" in response.json

    def test_calculate_mileage_invalid_locations(self, client):
        response = client.post(
            "/mileage", json={"start": "", "end": "", "purpose": "Test"}
        )
        assert response.status_code == 400
        assert "error" in response.json

    def test_add_mileage_record_success(self, client, mock_google_api):
        mock_google_api.return_value.json.return_value = {
            "status": "OK",
            "routes": [{"legs": [{"distance": {"text": "15.0 mi"}}]}],
        }

        response = client.post(
            "/mileage/add",
            json={
                "user_id": 123,
                "start_location": "Start St",
                "end_location": "End Ave",
                "date": "2023-12-01",
            },
        )

        assert response.status_code == 201
        assert "message" in response.json
        assert "data" in response.json

    def test_bulk_mileage_upload_success(self, client, mock_google_api):
        mock_google_api.return_value.json.return_value = {
            "status": "OK",
            "routes": [{"legs": [{"distance": {"text": "10.0 mi"}}]}],
        }

        response = client.post(
            "/mileage/bulk",
            json={
                "records": [
                    {"start": "Start St", "end": "End Ave", "date": "2023-12-01"},
                    {"start": "Other St", "end": "Final Ave", "date": "2023-12-02"},
                ]
            },
        )

        assert response.status_code == 200
        assert "success" in response.json
        assert response.json["success"] == 2

    def test_add_recurring_trip_success(self, client):
        response = client.post(
            "/mileage/recurring",
            json={
                "user_id": 123,
                "start": "Start St",
                "end": "End Ave",
                "frequency": "weekly",
                "purpose": "Client Meeting",
            },
        )

        assert response.status_code == 201
        assert "message" in response.json
        assert "trip_id" in response.json

    def test_get_mileage_summary_success(self, client):
        response = client.get("/mileage/summary?user_id=123&year=2023")
        assert response.status_code == 200
        assert "total_miles" in response.json
        assert "tax_deduction" in response.json
        assert "total_trips" in response.json

    def test_export_mileage_csv_success(self, client):
        response = client.get("/mileage/export?user_id=123&format=csv&year=2023")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv"
        assert "attachment" in response.headers["Content-Disposition"]

    def test_validate_business_purpose(self, client):
        response = client.post(
            "/mileage",
            json={
                "start": "Start St",
                "end": "End Ave",
                "purpose": "Personal Trip",  # Non-business purpose
            },
        )
        assert response.status_code == 400
        assert "error" in response.json

    def test_calculate_tax_deduction(self, client, mock_google_api):
        mock_google_api.return_value.json.return_value = {
            "status": "OK",
            "routes": [{"legs": [{"distance": {"text": "100.0 mi"}}]}],
        }

        response = client.post(
            "/mileage",
            json={"start": "Start St", "end": "End Ave", "purpose": "Business Meeting"},
        )

        assert response.status_code == 200
        assert "tax_deduction" in response.json
        # Verify tax deduction calculation (100 miles * IRS rate)
        assert response.json["tax_deduction"] == 100.0 * 0.655

    def test_recurring_trip_scheduling(self, client):
        response = client.post(
            "/mileage/recurring",
            json={
                "user_id": 123,
                "start": "Start St",
                "end": "End Ave",
                "frequency": "daily",
                "purpose": "Office Commute",
            },
        )

        assert response.status_code == 201
        assert "trip_id" in response.json

        # Verify scheduled trips
        scheduled_response = client.get("/mileage/recurring/scheduled?user_id=123")
        assert scheduled_response.status_code == 200
        assert len(scheduled_response.json["scheduled_trips"]) > 0

    def test_mileage_rate_updates(self, client, mock_google_api):
        # Test with different IRS rates
        with patch("api.routes.mileage_routes.IRS_MILEAGE_RATE", 0.67):
            mock_google_api.return_value.json.return_value = {
                "status": "OK",
                "routes": [{"legs": [{"distance": {"text": "10.0 mi"}}]}],
            }

            response = client.post(
                "/mileage",
                json={"start": "Start St", "end": "End Ave", "purpose": "Business"},
            )

            assert response.status_code == 200
            assert response.json["tax_deduction"] == 10.0 * 0.67

    def test_distance_calculation_methods(self, client):
        # Test different distance calculation methods
        response = client.post(
            "/mileage/calculate",
            json={
                "start": "Start St",
                "end": "End Ave",
                "calculation_method": "straight_line",
            },
        )
        assert response.status_code == 200
        assert "distance" in response.json

        response = client.post(
            "/mileage/calculate",
            json={
                "start": "Start St",
                "end": "End Ave",
                "calculation_method": "driving",
            },
        )
        assert response.status_code == 200
        assert "distance" in response.json
