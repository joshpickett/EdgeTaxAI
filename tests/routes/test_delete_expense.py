def test_delete_expense_success(client):
    """Test deleting an existing expense."""
    response = client.delete("/delete/1")
    assert response.status_code == 200
    assert b"Expense deleted successfully" in response.data


def test_delete_expense_not_found(client):
    """Test deleting a non-existing expense."""
    response = client.delete("/delete/999")
    assert response.status_code == 404
    assert b"Expense not found" in response.data
