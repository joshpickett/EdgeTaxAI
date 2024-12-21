def test_add_mileage_invalid_user_id(client):
    response = client.post(
        "/mileage/add",
        json={
            "user_id": 999,
            "start_location": "Location A",
            "end_location": "Location B",
            "date": "2024-12-20"
        }
    )
    assert response.status_code == 404
    assert "User not found" in response.json["error"]
