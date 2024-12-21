def test_add_mileage_invalid_date(client):
    response = client.post(
        "/mileage/add",
        json={
            "user_id": 1,
            "start_location": "Location A",
            "end_location": "Location B",
            "date": "2024-13-01"
        }
    )
    assert response.status_code == 400
    assert "Invalid date format" in response.json["error"]
