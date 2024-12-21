def test_edit_expense_success(client):
    """Test editing an existing expense."""
    response = client.put("/edit/1", json={"description": "Updated Expense"})
    assert response.status_code == 200
    assert b"Expense updated successfully" in response.data

def test_edit_expense_not_found(client):
    """Test editing a non-existing expense."""
    response = client.put("/edit/999", json={"description": "New"})
    assert response.status_code == 404
    assert b"Expense not found" in response.data
