import pytest
from flask import Flask
from ...routes.tax_optimization_routes import tax_optimization_bp
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.register_blueprint(tax_optimization_bp)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_optimize_tax_strategy(client):
    """Test tax optimization strategy endpoint"""
    with patch('api.routes.tax_optimization_routes.analyze_optimization_opportunities') as mock_analyze:
        mock_analyze.return_value = {
            'potential_deductions': 5000.00,
            'suggestions': ['Track mileage', 'Keep receipts'],
            'potential_savings': 1250.00
        }
        
        response = client.post('/tax/optimize', json={
            'user_id': 1,
            'year': 2023
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'optimization_suggestions' in data
        assert 'potential_savings' in data['optimization_suggestions']

def test_analyze_deductions(client):
    """Test deduction analysis endpoint"""
    response = client.post('/analyze-deductions', json={
        'user_id': 1,
        'year': 2023
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'optimization_suggestions' in data
    assert 'potential_savings' in data
    assert 'recommended_actions' in data

def test_enhanced_analyze(client):
    """Test enhanced analysis endpoint"""
    response = client.post('/enhanced-analyze', json={
        'user_id': 1,
        'quarter': 1,
        'expense_data': [
            {'description': 'Gas', 'amount': 50.00},
            {'description': 'Office supplies', 'amount': 100.00}
        ]
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'optimization_suggestions' in data
    assert 'potential_savings' in data

def test_analyze_deductions_invalid_user(client):
    """Test deduction analysis with invalid user"""
    response = client.post('/analyze-deductions', json={
        'year': 2023
    })
    
    assert response.status_code == 400
    assert 'error' in response.get_json()

def test_enhanced_analyze_invalid_data(client):
    """Test enhanced analysis with invalid data"""
    response = client.post('/enhanced-analyze', json={
        'user_id': 1,
        'quarter': 1
    })
    
    assert response.status_code == 400
    assert 'error' in response.get_json()
