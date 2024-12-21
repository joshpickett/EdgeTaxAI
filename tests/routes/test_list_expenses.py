def test_list_expenses_success(client):
    """Test listing expenses for a valid user."""
    response = client.get("/list/1")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_list_expenses_no_user(client):
    """Test listing expenses for a non-existing user."""
    response = client.get("/list/999")
    assert response.status_code == 200
    assert response.json == []
