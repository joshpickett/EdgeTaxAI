def test_fetch_mileage_no_trips(client):
    response = client.get("/mileage/fetch?user_id=1")
    assert response.status_code == 200
    assert response.json["data"] == []
