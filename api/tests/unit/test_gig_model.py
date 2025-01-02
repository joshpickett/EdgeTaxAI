import pytest
import sqlite3
import os
from ...models.gig_model import init_gig_table


@pytest.fixture
def test_database():
    """Create a temporary test database"""
    test_database_path = "test_database.db"
    if os.path.exists(test_database_path):
        os.remove(test_database_path)

    # Set environment variable for test database
    os.environ["DB_PATH"] = test_database_path

    yield test_database_path

    # Cleanup
    if os.path.exists(test_database_path):
        os.remove(test_database_path)


def test_init_gig_table(test_database):
    """Test creating the connected_platforms table"""
    # Initialize the table
    init_gig_table()

    # Verify table was created
    connection = sqlite3.connect(test_database)
    cursor = connection.cursor()

    # Check if table exists
    cursor.execute(
        """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='connected_platforms'
    """
    )

    assert cursor.fetchone() is not None

    # Verify table structure
    cursor.execute("PRAGMA table_info(connected_platforms)")
    columns = cursor.fetchall()

    expected_columns = {
        "id": "INTEGER",
        "user_id": "INTEGER",
        "platform": "TEXT",
        "access_token": "TEXT",
        "refresh_token": "TEXT",
        "created_at": "TIMESTAMP",
    }

    for column in columns:
        name = column[1]
        type_ = column[2]
        assert name in expected_columns
        assert expected_columns[name] in type_

    connection.close()


def test_init_gig_table_idempotent(test_database):
    """Test that calling init_gig_table multiple times is safe"""
    # Call init multiple times
    init_gig_table()
    init_gig_table()

    # Verify only one table exists
    connection = sqlite3.connect(test_database)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT count(*) FROM sqlite_master 
        WHERE type='table' AND name='connected_platforms'
    """
    )

    assert cursor.fetchone()[0] == 1
    connection.close()
