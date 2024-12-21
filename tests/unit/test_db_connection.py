import os
import sqlite3
from api.routes.auth_routes import get_db_connection


def test_db_connection():
    """Test if the database connection is established successfully."""
    conn = None
    try:
        conn = get_db_connection()
        assert conn is not None, "Failed to establish database connection."
    finally:
        if conn:
            conn.close()
