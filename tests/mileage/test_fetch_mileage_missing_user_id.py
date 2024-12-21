def test_fetch_mileage_missing_user_id(client):
    response = client.get("/mileage/fetch")
    assert response.status_code == 400
    assert "Missing user_id" in response.json["error"]
