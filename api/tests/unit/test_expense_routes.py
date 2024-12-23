import pytest
from flask import Flask
from datetime import datetime, timedelta
from ...routes.expense_routes import expense_blueprint
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(expense_blueprint)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_get_expense_summary(client):
    """Test getting expense summary"""
    with patch('api.routes.expense_routes.report_generator') as mock_generator:
        # Mock the report generator
        mock_generator.generate_expense_summary.return_value = {
            'total': 1000.00,
            'categories': {
                'gas': 300.00,
                'maintenance': 700.00
            }
        }
        
        # Make request
        response = client.get('/expenses/summary?user_id=1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['total'] == 1000.00
        assert 'categories' in data
        assert len(data['categories']) == 2

def test_create_expense(client):
    """Test creating a new expense"""
    with patch('api.routes.expense_routes.get_db_connection') as mock_db, \
         patch('api.routes.expense_routes.categorize_expense') as mock_categorize:
        
        # Mock database connection
        mock_cursor = MagicMock()
        mock_db.return_value.cursor.return_value = mock_cursor
        
        # Mock expense categorization
        mock_categorize.return_value = {
            'category': 'vehicle',
            'confidence_score': 0.95
        }
        
        # Test data
        expense_data = {
            'description': 'Oil change',
            'amount': 45.99,
            'source': 'manual'
        }
        
        # Make request
        response = client.post('/expenses', json=expense_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['description'] == 'Oil change'
        assert mock_cursor.execute.called

def test_create_platform_expense(client):
    """Test creating an expense from a gig platform"""
    with patch('api.routes.expense_routes.get_db_connection') as mock_db, \
         patch('api.routes.expense_routes.analyze_tax_context') as mock_tax:
        
        # Mock database
        mock_cursor = MagicMock()
        mock_db.return_value.cursor.return_value = mock_cursor
        
        # Mock tax analysis
        mock_tax.return_value = {
            'deductible': True,
            'category': 'vehicle_expense'
        }
        
        # Test data
        expense_data = {
            'description': 'Platform fee',
            'amount': 25.00,
            'platform_source': 'uber',
            'platform_trip_id': '12345'
        }
        
        # Make request
        response = client.post('/expenses', json=expense_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['tax_analysis']['deductible'] == True
        assert mock_cursor.execute.called
