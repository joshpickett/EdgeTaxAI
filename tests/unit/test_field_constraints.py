import sys
import os
import sqlite3
import pytest

# Add the 'api/models' directory to the Python module search path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models"))
)

from gig_model import init_gig_table


def test_missing_required_fields():
    init_gig_table()
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            "INSERT INTO connected_platforms (platform) VALUES ('TestPlatform')"
        )
    conn.close()
