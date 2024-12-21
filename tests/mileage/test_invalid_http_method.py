def test_invalid_http_method(client):
    response = client.put("/mileage/add")
    assert response.status_code == 405
    assert "Method Not Allowed" in response.json["error"]
