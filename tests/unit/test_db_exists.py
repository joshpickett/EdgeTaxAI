import sys
import os
import sqlite3

# Add the 'api/models' directory to the Python module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models")))

from gig_model import init_gig_table

def test_database_already_exists():
    # Define the database file name
    db_path = "database.db"
    
    # Step 1: Ensure database file exists
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.close()

    # Step 2: Run the script to initialize the table
    try:
        init_gig_table()
    except Exception as e:
        assert False, f"Script failed when database already exists: {e}"

    # Step 3: Verify the database file still exists
    assert os.path.exists(db_path), "Database file was removed or altered unexpectedly."

    # Cleanup: Optionally remove the database after test (uncomment if needed)
    # os.remove(db_path)
