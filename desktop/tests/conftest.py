import pytest
import os
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime

@pytest.fixture
def mock_api_response():
    return {
        "status": "success",
        "data": {
            "user_id": 123,
            "token": "test_token"
        }
    }

@pytest.fixture
def mock_platform_data():
    return {
        "connected_accounts": [
            {
                "platform": "uber",
                "last_sync": datetime.now().isoformat(),
                "status": "active"
            }
        ],
        "earnings": 1000.00,
        "trips": [
            {
                "id": "trip1",
                "date": "2023-01-01",
                "amount": 50.00
            }
        ]
    }

@pytest.fixture
def mock_token_storage():
    class MockTokenStorage:
        def __init__(self):
            self.store = {}
        
        def store_token(self, user_id, platform, token_data):
            self.store[(user_id, platform)] = token_data
            return True
            
        def get_token(self, user_id, platform):
            return self.store.get((user_id, platform))
            
        def delete_token(self, user_id, platform):
            if (user_id, platform) in self.store:
                del self.store[(user_id, platform)]
                return True
            return False
    
    return MockTokenStorage()

@pytest.fixture
def mock_requests():
    class MockResponse:
        def __init__(self, status_code=200, json_data=None):
            self.status_code = status_code
            self._json_data = json_data or {}
            
        def json(self):
            return self._json_data
            
    return MockResponse

@pytest.fixture
def test_env_vars():
    os.environ["API_BASE_URL"] = "http://test-api.com"
    os.environ["SECRET_KEY"] = "test-secret-key"
    yield
    del os.environ["API_BASE_URL"]
    del os.environ["SECRET_KEY"]
