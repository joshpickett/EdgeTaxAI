import sys
import os

# Add the 'api/models' directory to the Python module search path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../api/models"))
)

from gig_model import init_gig_table


def test_db_initialization():
    db_path = "database.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    init_gig_table()
    assert os.path.exists(db_path)
