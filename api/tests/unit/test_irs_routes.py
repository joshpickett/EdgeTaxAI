import pytest
from flask import Flask
from ...routes.irs_routes import irs_bp
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(irs_bp)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_generate_schedule_c(client):
    """Test generating Schedule C form data"""
    with patch('api.routes.irs_routes.get_db_connection') as mock_db:
        # Mock cursor and database connection
        mock_cursor = MagicMock()
        mock_db.return_value.cursor.return_value = mock_cursor
        
        # Mock expense data
        mock_cursor.fetchall.return_value = [
            ('advertising', 500.00),
            ('car_expenses', 1000.00),
            ('supplies', 300.00)
        ]
        
        # Make request
        response = client.post('/generate-schedule-c', json={
            'user_id': 1,
            'year': 2023
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'expenses' in data
        assert 'total_expenses' in data
        assert data['total_expenses'] == 1800.00

def test_generate_schedule_c_no_user_id(client):
    """Test generating Schedule C without user ID"""
    response = client.post('/generate-schedule-c', json={
        'year': 2023
    })
    
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_generate_schedule_c_db_error(client):
    """Test handling database errors"""
    with patch('api.routes.irs_routes.get_db_connection') as mock_db:
        mock_db.side_effect = Exception("Database error")
        
        response = client.post('/generate-schedule-c', json={
            'user_id': 1,
            'year': 2023
        })
        
        assert response.status_code == 500
        assert 'error' in response.get_json()
