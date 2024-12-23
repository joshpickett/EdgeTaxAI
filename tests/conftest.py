import pytest
from api.app import create_app
from api.utils.db_utils import Database
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture
def db():
    """Create a new database for each test."""
    db = Database()
    yield db
    db.close()
