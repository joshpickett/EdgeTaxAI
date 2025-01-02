import os
import sys
from typing import Optional, Union
from pathlib import Path


def setup_desktop_path(file_path: Optional[Union[str, Path]] = None) -> None:
    """Set up Python path for desktop application components"""
    if file_path:
        current_dir = Path(file_path).parent
    else:
        current_dir = Path(__file__).parent

    # Add project root to path
    project_root = current_dir.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Add desktop-specific paths
    desktop_path = project_root / "desktop"
    if str(desktop_path) not in sys.path:
        sys.path.insert(0, str(desktop_path))

    # Add shared components path
    shared_path = project_root / "shared"
    if str(shared_path) not in sys.path:
        sys.path.insert(0, str(shared_path))


def get_desktop_root() -> Path:
    """Get the desktop application root directory"""
    return Path(__file__).parent


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent
