"""
Desktop Utils Package
Contains utility functions and classes for the desktop application
"""
from desktop.setup_path import setup_desktop_path
setup_desktop_path()

from .sync_manager import SyncManager
from .error_handler import handle_api_error

__all__ = [
    'SyncManager',
    'handle_api_error'
]
