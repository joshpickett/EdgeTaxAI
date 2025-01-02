import pytest
from flask import Flask
from ...routes.mileage_routes import mileage_bp
from unittest.mock import patch, MagicMock


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(mileage_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


def test_calculate_mileage(client):
    """Test mileage calculation endpoint"""
    with patch("api.routes.mileage_routes.fetch_google_directions") as mock_directions:
        # Mock Google Directions API response
        mock_directions.return_value = ("10 mi", None)

        response = client.post(
            "/mileage",
            json={
                "start": "123 Start St",
                "end": "456 End Ave",
                "purpose": "business meeting",
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["distance"] == "10 mi"
        assert "tax_deduction" in data


def test_calculate_mileage_invalid_locations(client):
    """Test mileage calculation with invalid locations"""
    response = client.post(
        "/mileage",
        json={"start": "", "end": "456 End Ave", "purpose": "business meeting"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_add_mileage_record(client):
    """Test adding mileage record"""
    with patch("api.routes.mileage_routes.get_db_connection") as mock_db, patch(
        "api.routes.mileage_routes.fetch_google_directions"
    ) as mock_directions:

        # Mock database connection
        mock_cursor = MagicMock()
        mock_db.return_value.cursor.return_value = mock_cursor

        # Mock directions API
        mock_directions.return_value = ("10 mi", None)

        response = client.post(
            "/mileage/add",
            json={
                "user_id": 1,
                "start_location": "123 Start St",
                "end_location": "456 End Ave",
                "date": "2023-01-01",
            },
        )

        assert response.status_code == 201
        assert mock_cursor.execute.called


def test_bulk_mileage_upload(client):
    """Test bulk mileage upload"""
    with patch("api.routes.mileage_routes.fetch_google_directions") as mock_directions:
        mock_directions.return_value = ("10 mi", None)

        response = client.post(
            "/mileage/bulk",
            json={
                "records": [
                    {
                        "start": "123 Start St",
                        "end": "456 End Ave",
                        "date": "2023-01-01",
                    },
                    {
                        "start": "789 Other St",
                        "end": "321 Final Ave",
                        "date": "2023-01-02",
                    },
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == 2
        assert len(data["successful_records"]) == 2
