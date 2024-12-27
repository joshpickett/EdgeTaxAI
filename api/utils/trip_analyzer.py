import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, List, Any, Optional
from utils.db_utils import get_db_connection
from utils.error_handler import handle_api_error

...rest of the code...
