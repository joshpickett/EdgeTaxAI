import pytest
from api.app import create_app
import logging

@pytest.fixture
def app():
    """Create and configure test app instance"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_app_creation(app):
    """Test app creation and configuration"""
    assert app is not None
    assert app.config['TESTING'] is True

def test_registered_blueprints(app):
    """Test all required blueprints are registered"""
    blueprints = [
        'auth_bp',
        'expense_bp', 
        'reports_bp',
        'bank_bp',
        'tax_bp',
        'mileage_bp',
        'ocr_bp',
        'platform_bp',
        'analytics_bp'
    ]
    
    for blueprint in blueprints:
        assert blueprint in app.blueprints

def test_error_handler_registration(app):
    """Test error handlers are registered"""
    assert app.error_handler_spec[None][None]

def test_cors_enabled(app):
    """Test CORS is enabled"""
    assert app.config['CORS_HEADERS'] == 'Content-Type'

def test_logging_configuration(app):
    """Test logging is properly configured"""
    assert logging.getLogger().level == logging.INFO

def test_404_handler(client):
    """Test 404 error handler"""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    assert b'Not Found' in response.data

def test_500_handler(client, mocker):
    """Test 500 error handler"""
    # Mock an endpoint that raises an error
    @app.route('/test-error')
    def test_error():
        raise Exception('Test error')
        
    response = client.get('/test-error')
    assert response.status_code == 500
    assert b'Internal Server Error' in response.data
