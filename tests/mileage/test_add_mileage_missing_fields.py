def test_add_mileage_missing_fields(client):
    response = client.post(
        "/mileage/add", json={"user_id": 1, "start_location": "Location A"}
    )
    assert response.status_code == 400
    assert "Missing required fields" in response.json["error"]
