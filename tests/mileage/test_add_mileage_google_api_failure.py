def test_add_mileage_google_api_failure(client, mock_google_api_failure):
    response = client.post(
        "/mileage/add",
        json={
            "user_id": 1,
            "start_location": "Location A",
            "end_location": "Location B",
            "date": "2024-12-20"
        }
    )
    assert response.status_code == 500
    assert "Failed to calculate distance" in response.json["error"]
