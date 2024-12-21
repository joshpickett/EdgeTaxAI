def test_fetch_mileage_invalid_user_id(client):
    response = client.get("/mileage/fetch?user_id=999")
    assert response.status_code == 404
    assert "User not found" in response.json["error"]
