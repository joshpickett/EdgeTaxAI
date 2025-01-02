import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from api.utils.audit_trail import AuditTrail


@pytest.fixture
def audit_trail():
    return AuditTrail()


@pytest.fixture
def mock_db_connection():
    mock_connection = Mock()
    mock_cursor = Mock()
    mock_connection.cursor.return_value = mock_cursor
    return mock_connection


def test_log_category_change_success(audit_trail, mock_db_connection):
    """Test successful logging of category changes"""
    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        result = audit_trail.log_category_change(
            expense_id=1,
            old_category="Food",
            new_category="Transportation",
            user_id=1,
            confidence_score=0.95,
        )

        mock_db_connection.cursor().execute.assert_called_once()
        mock_db_connection.commit.assert_called_once()
        assert result is None


def test_log_category_change_error(audit_trail, mock_db_connection):
    """Test error handling in category change logging"""
    mock_db_connection.cursor.side_effect = Exception("Database error")

    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        with patch("logging.error") as mock_logging:
            audit_trail.log_category_change(
                expense_id=1,
                old_category="Food",
                new_category="Transportation",
                user_id=1,
                confidence_score=0.95,
            )

            mock_logging.assert_called_once()


def test_get_audit_trail_success(audit_trail, mock_db_connection):
    """Test successful retrieval of audit trail"""
    mock_db_connection.cursor().fetchall.return_value = [
        {
            "expense_id": 1,
            "old_category": "Food",
            "new_category": "Transportation",
            "user_id": 1,
            "confidence_score": 0.95,
            "timestamp": datetime.now().isoformat(),
        }
    ]

    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        result = audit_trail.get_audit_trail(expense_id=1)

        assert len(result) == 1
        assert result[0]["expense_id"] == 1
        assert result[0]["old_category"] == "Food"


def test_get_audit_trail_with_filters(audit_trail, mock_db_connection):
    """Test audit trail retrieval with filters"""
    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        audit_trail.get_audit_trail(expense_id=1, user_id=2)

        # Verify SQL query includes both filters
        call_args = mock_db_connection.cursor().execute.call_args[0]
        assert "expense_id = ?" in call_args[0]
        assert "user_id = ?" in call_args[0]


def test_get_audit_trail_error(audit_trail, mock_db_connection):
    """Test error handling in audit trail retrieval"""
    mock_db_connection.cursor.side_effect = Exception("Database error")

    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        with patch("logging.error") as mock_logging:
            result = audit_trail.get_audit_trail()

            assert result == []
            mock_logging.assert_called_once()


def test_audit_trail_empty_result(audit_trail, mock_db_connection):
    """Test handling of empty audit trail results"""
    mock_db_connection.cursor().fetchall.return_value = []

    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        result = audit_trail.get_audit_trail()

        assert result == []


def test_audit_trail_data_validation(audit_trail, mock_db_connection):
    """Test data validation in audit trail logging"""
    with patch(
        "api.utils.audit_trail.get_db_connection", return_value=mock_db_connection
    ):
        audit_trail.log_category_change(
            expense_id=1,
            old_category=None,  # Test with None value
            new_category="Transportation",
            user_id=1,
            confidence_score=0.95,
        )

        # Verify the execution still happened
        mock_db_connection.cursor().execute.assert_called_once()
