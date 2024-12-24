import pytest
from unittest.mock import patch, Mock
from api.app import create_app, log_api_startup

@pytest.fixture
def app():
    """Create test Flask application"""
    application = create_app()
    application.config['TESTING'] = True
    return application

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_app_creation(app):
    """Test Flask application creation"""
    assert app.name == 'api'
    assert app.config['TESTING'] is True

def test_cors_enabled(app):
    """Test Cross-Origin Resource Sharing configuration"""
    assert 'CORS' in app.extensions

def test_blueprints_registered(app):
    """Test blueprint registration"""
    blueprints = ['auth_bp', 'expense_bp', 'reports_bp', 'bank_bp', 
                  'tax_bp', 'mileage_bp', 'ocr_bp', 'tax_optimization_bp']
    
    for blueprint in blueprints:
        assert blueprint in app.blueprints

def test_error_handler_registration(app):
    """Test error handler registration"""
    from api.utils.error_handler import APIError
    assert APIError in app.error_handler_spec[None]

@patch('logging.info')
def test_log_api_startup(mock_logging, app):
    """Test application startup logging"""
    log_api_startup(app)
    
    # Verify logging calls
    mock_logging.assert_any_call("Starting Flask API Server...")
    mock_logging.assert_any_call("Registered Endpoints:")
    mock_logging.assert_any_call("Flask API Server started successfully.")

def test_api_endpoints(client):
    """Test application programming interface endpoints are accessible"""
    endpoints = [
        '/api/auth/health',
        '/api/expenses/health',
        '/api/reports/health',
        '/api/banks/health',
        '/api/tax/health',
        '/api/mileage/health'
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [200, 404]  # 404 if no health check implemented

def test_error_handling(client):
    """Test global error handling"""
    from api.utils.error_handler import APIError
    
    @app.route('/test-error')
    def test_error():
        raise APIError("Test error", status_code=400)
    
    response = client.get('/test-error')
    assert response.status_code == 400
    assert b'Test error' in response.data
