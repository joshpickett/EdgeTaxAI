import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from ..routes.irs_routes import irs_bp

@pytest.fixture
def app():
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(irs_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_database():
    with patch('sqlite3.connect') as mock:
        yield mock

class TestIRSRoutes:
    def test_generate_schedule_c_success(self, client, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('office_supplies', 1000.00),
            ('travel', 2000.00)
        ]

        response = client.post('/generate-schedule-c',
                             json={
                                 'user_id': 123,
                                 'year': 2023
                             })
        
        assert response.status_code == 200
        data = response.json
        assert 'expenses' in data
        assert 'total_expenses' in data

    def test_generate_schedule_c_missing_user(self, client):
        response = client.post('/generate-schedule-c',
                             json={'year': 2023})
        assert response.status_code == 400
        assert 'error' in response.json

    def test_quarterly_estimate_success(self, client, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(5000.00,), (2000.00,)]

        response = client.post('/quarterly-estimate',
                             json={
                                 'user_id': 123,
                                 'quarter': 1,
                                 'year': 2023
                             })
        
        assert response.status_code == 200
        data = response.json
        assert 'estimated_tax' in data
        assert 'net_income' in data

    def test_quarterly_estimate_invalid_quarter(self, client):
        response = client.post('/quarterly-estimate',
                             json={
                                 'user_id': 123,
                                 'quarter': 5,
                                 'year': 2023
                             })
        assert response.status_code == 400
        assert 'error' in response.json

    def test_calculate_deductions_success(self, client, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('car_expenses', 1000.00),
            ('office_supplies', 500.00)
        ]

        response = client.post('/calculate-deductions',
                             json={
                                 'user_id': 123,
                                 'year': 2023
                             })
        
        assert response.status_code == 200
        assert 'deductions' in response.json
        assert 'total_deductions' in response.json

    def test_tax_category_validation(self, client):
        response = client.post('/validate-category',
                             json={
                                 'category': 'invalid_category',
                                 'amount': 100.00
                             })
        assert response.status_code == 400
        assert 'error' in response.json

    def test_expense_categorization(self, client):
        response = client.post('/categorize-expense',
                             json={
                                 'description': 'Office supplies from Staples',
                                 'amount': 150.00
                             })
        assert response.status_code == 200
        assert 'category' in response.json

    def test_tax_summary_generation(self, client, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ('income', 50000.00),
            ('expenses', 20000.00)
        ]

        response = client.get('/tax-summary?user_id=123&year=2023')
        assert response.status_code == 200
        assert 'total_income' in response.json
        assert 'total_expenses' in response.json
        assert 'net_income' in response.json

    def test_estimated_payments_calculation(self, client):
        response = client.post('/estimated-payments',
                             json={
                                 'income': 50000.00,
                                 'expenses': 20000.00,
                                 'quarter': 1
                             })
        assert response.status_code == 200
        assert 'payment_amount' in response.json
        assert 'due_date' in response.json

    def test_deduction_limits_validation(self, client):
        response = client.post('/validate-deduction',
                             json={
                                 'category': 'meals',
                                 'amount': 100000.00  # Exceeds reasonable limit
                             })
        assert response.status_code == 400
        assert 'error' in response.json
