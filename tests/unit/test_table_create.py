import sys
import os
import sqlite3

# Add the 'api/models' directory to the Python module search path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models"))
)

from gig_model import init_gig_table


def test_table_creation():
    """Test that the connected_platforms table is created successfully."""
    DB_PATH = "database.db"
    init_gig_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='connected_platforms';"
    )
    result = cursor.fetchone()
    assert result is not None, "Table 'connected_platforms' was not created."
    conn.close()
