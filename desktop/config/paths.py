"""
Desktop application path configuration
"""
from pathlib import Path
from desktop.setup_path import get_desktop_root, get_project_root

DESKTOP_ROOT = get_desktop_root()
PROJECT_ROOT = get_project_root()
SHARED_ROOT = PROJECT_ROOT / 'shared'
ASSETS_ROOT = PROJECT_ROOT / 'assets'
CONFIG_ROOT = DESKTOP_ROOT / 'config'

# Service-specific paths
SERVICES_ROOT = DESKTOP_ROOT / 'services'
UTILS_ROOT = DESKTOP_ROOT / 'utils'

# Data paths
DATA_ROOT = DESKTOP_ROOT / 'data'
CACHE_ROOT = DATA_ROOT / 'cache'
LOGS_ROOT = DATA_ROOT / 'logs'

# Ensure required directories exist
for path in [DATA_ROOT, CACHE_ROOT, LOGS_ROOT]:
    path.mkdir(parents=True, exist_ok=True)
