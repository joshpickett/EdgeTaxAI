import pytest
from unittest.mock import patch, Mock, MagicMock
from api.utils.db_utils import Database, DatabaseError, get_db_connection
from api.utils.db_utils import (
    generate_one_time_password,
    save_one_time_password_for_user,
    verify_one_time_password_for_user,
)
import sqlite3


@pytest.fixture
def mock_database():
    return Mock(spec=Database)


@pytest.fixture
def mock_connection():
    return Mock(spec=sqlite3.Connection)


@pytest.fixture
def mock_cursor():
    return Mock(spec=sqlite3.Cursor)


def test_database_connection(mock_connection):
    """Test database connection context manager"""
    with patch("sqlite3.connect", return_value=mock_connection):
        db = Database("test.db")
        with db.get_connection() as connection:
            assert connection == mock_connection
        mock_connection.close.assert_called_once()


def test_database_connection_error():
    """Test database connection error handling"""
    with patch("sqlite3.connect", side_effect=sqlite3.Error("Connection failed")):
        db = Database("test.db")
        with pytest.raises(DatabaseError):
            with db.get_connection():
                pass


def test_cursor_context_manager(mock_connection, mock_cursor):
    """Test cursor context manager"""
    mock_connection.cursor.return_value = mock_cursor
    with patch("sqlite3.connect", return_value=mock_connection):
        db = Database("test.db")
        with db.get_cursor() as cursor:
            assert cursor == mock_cursor
        mock_connection.commit.assert_called_once()


def test_generate_one_time_password():
    """Test one time password generation"""
    one_time_password = generate_one_time_password()
    assert len(one_time_password) == 6
    assert one_time_password.isdigit()


def test_save_one_time_password_for_user(mock_database, mock_cursor):
    """Test saving one time password for user"""
    mock_database.cursor.return_value = mock_cursor
    with patch("api.utils.db_utils.Database", return_value=mock_database):
        result = save_one_time_password_for_user("test@example.com", "123456")
        assert mock_cursor.execute.called
        mock_database.commit.assert_called_once()


def test_verify_one_time_password_for_user_success(mock_database, mock_cursor):
    """Test successful one time password verification"""
    mock_cursor.fetchone.return_value = ("123456", "2099-12-31 23:59:59")
    mock_database.cursor.return_value = mock_cursor
    with patch("api.utils.db_utils.Database", return_value=mock_database):
        result = verify_one_time_password_for_user("test@example.com", "123456")
        assert result is True


def test_verify_one_time_password_for_user_invalid(mock_database, mock_cursor):
    """Test invalid one time password verification"""
    mock_cursor.fetchone.return_value = ("654321", "2099-12-31 23:59:59")
    mock_database.cursor.return_value = mock_cursor
    with patch("api.utils.db_utils.Database", return_value=mock_database):
        result = verify_one_time_password_for_user("test@example.com", "123456")
        assert result is False


def test_verify_one_time_password_for_user_expired(mock_database, mock_cursor):
    """Test expired one time password verification"""
    mock_cursor.fetchone.return_value = ("123456", "2000-01-01 00:00:00")
    mock_database.cursor.return_value = mock_cursor
    with patch("api.utils.db_utils.Database", return_value=mock_database):
        result = verify_one_time_password_for_user("test@example.com", "123456")
        assert result is False


def test_get_db_connection():
    """Test database connection creation"""
    with patch("sqlite3.connect") as mock_connect:
        connection = get_db_connection()
        mock_connect.assert_called_once()
