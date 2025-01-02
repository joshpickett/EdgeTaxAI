import pytest
from unittest.mock import Mock, patch
import json
import os
from datetime import datetime, timedelta
from api.utils.session_manager import SessionManager


@pytest.fixture
def session_manager():
    """Create a session manager instance with a temporary directory"""
    test_directory = ".test_sessions"
    manager = SessionManager(test_directory)
    yield manager
    # Cleanup after tests
    if os.path.exists(test_directory):
        for file in os.listdir(test_directory):
            os.remove(os.path.join(test_directory, file))
        os.rmdir(test_directory)


@pytest.fixture
def sample_session_data():
    """Sample session data for testing"""
    return {"preferences": {"theme": "dark"}, "last_login": datetime.now().isoformat()}


def test_create_session_success(session_manager, sample_session_data):
    """Test successful session creation"""
    result = session_manager.create_session(1, sample_session_data)
    assert result is True

    session_file = os.path.join(session_manager.session_directory, "session_1.json")
    assert os.path.exists(session_file)

    with open(session_file, "r") as file:
        stored_data = json.load(file)
        assert stored_data["user_id"] == 1
        assert stored_data["data"] == sample_session_data


def test_get_session_success(session_manager, sample_session_data):
    """Test successful session retrieval"""
    session_manager.create_session(1, sample_session_data)
    session = session_manager.get_session(1)

    assert session is not None
    assert session["data"] == sample_session_data
    assert "created_at" in session
    assert "expires_at" in session


def test_get_session_expired(session_manager, sample_session_data):
    """Test expired session retrieval"""
    # Create session with expired timestamp
    session_data = {
        "user_id": 1,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        "data": sample_session_data,
    }

    session_file = os.path.join(session_manager.session_directory, "session_1.json")
    os.makedirs(session_manager.session_directory, exist_ok=True)
    with open(session_file, "w") as file:
        json.dump(session_data, file)

    session = session_manager.get_session(1)
    assert session is None
    assert not os.path.exists(session_file)  # Should be deleted


def test_update_session_success(session_manager, sample_session_data):
    """Test successful session update"""
    session_manager.create_session(1, sample_session_data)

    update_data = {"preferences": {"theme": "light"}}
    result = session_manager.update_session(1, update_data)

    assert result is True
    updated_session = session_manager.get_session(1)
    assert updated_session["data"]["preferences"]["theme"] == "light"


def test_update_session_nonexistent(session_manager):
    """Test updating non-existent session"""
    result = session_manager.update_session(999, {"test": "data"})
    assert result is False


def test_delete_session_success(session_manager, sample_session_data):
    """Test successful session deletion"""
    session_manager.create_session(1, sample_session_data)
    result = session_manager.delete_session(1)

    assert result is True
    session_file = os.path.join(session_manager.session_directory, "session_1.json")
    assert not os.path.exists(session_file)


def test_delete_session_nonexistent(session_manager):
    """Test deleting non-existent session"""
    result = session_manager.delete_session(999)
    assert result is True  # Should return True even if file doesn't exist


def test_session_directory_creation(session_manager):
    """Test session directory creation"""
    assert os.path.exists(session_manager.session_directory)


def test_error_handling(session_manager):
    """Test error handling in session operations"""
    with patch("builtins.open", side_effect=Exception("IO Error")):
        result = session_manager.create_session(1, {})
        assert result is False


def test_session_expiration_calculation(session_manager, sample_session_data):
    """Test session expiration time calculation"""
    session_manager.create_session(1, sample_session_data)
    session = session_manager.get_session(1)

    created = datetime.fromisoformat(session["created_at"])
    expires = datetime.fromisoformat(session["expires_at"])

    assert (
        expires - created
    ).total_seconds() == session_manager.session_duration * 3600
