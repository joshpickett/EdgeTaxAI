import sys
import os
import sqlite3
import pytest

# Add the 'api/models' directory to the Python module search path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models"))
)

from gig_model import init_gig_table

DB_PATH = "database.db"


@pytest.fixture
def setup_database():
    """Setup and teardown fixture to initialize the table."""
    init_gig_table()
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_null_refresh_token(setup_database):
    """Test that NULL values are allowed for refresh_token."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO connected_platforms (user_id, platform, access_token, refresh_token)
        VALUES (?, ?, ?, ?)
    """,
        (1, "TestPlatform", "TestAccessToken", None),
    )
    conn.commit()
    conn.close()
