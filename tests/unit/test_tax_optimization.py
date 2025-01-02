import pytest
from api.routes.tax_optimization_routes import calculate_tax_savings
from unittest.mock import patch


def test_calculate_tax_savings():
    with patch("api.routes.tax_optimization_routes.get_db_connection") as mock_db:
        mock_cursor = mock_db.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = [1000]  # Mock total expenses

        result = calculate_tax_savings(user_id=1, year=2024)
        assert result["total_expenses"] == 1000
        assert result["estimated_savings"] == 250  # 25% tax rate


def test_calculate_tax_savings_no_expenses():
    with patch("api.routes.tax_optimization_routes.get_db_connection") as mock_db:
        mock_cursor = mock_db.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = [0]

        result = calculate_tax_savings(user_id=1, year=2024)
        assert result["total_expenses"] == 0
        assert result["estimated_savings"] == 0
