import os
import sys
from typing import Optional


def setup_python_path(file_path: Optional[str] = None) -> None:
    """Set up Python path for both package and direct execution"""
    if file_path:
        current_dir = os.path.dirname(os.path.abspath(file_path))
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))

    project_root = os.path.dirname(os.path.dirname(current_dir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
