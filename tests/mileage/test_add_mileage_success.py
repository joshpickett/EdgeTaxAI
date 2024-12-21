import pytest

def test_add_mileage_success(client, mock_db):
    response = client.post(
        "/mileage/add",
        json={
            "user_id": 1,
            "start_location": "Location A",
            "end_location": "Location B",
            "date": "2024-12-20"
        }
    )
    assert response.status_code == 201
    assert "Mileage record added successfully" in response.json["message"]
