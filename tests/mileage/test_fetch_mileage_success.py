def test_fetch_mileage_success(client, mock_db_with_mileage):
    response = client.get("/mileage/fetch?user_id=1")
    assert response.status_code == 200
    assert len(response.json["data"]) > 0
