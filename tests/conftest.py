import pytest
from pathlib import Path

# Asset paths for testing
ASSETS_DIR = Path(__file__).parent.parent / 'assets'
TEST_LOGO = ASSETS_DIR / 'logo' / 'primary' / 'edgetaxai-horizontal-color.svg'
TEST_ICON = ASSETS_DIR / 'logo' / 'icon' / 'edgetaxai-icon-color.svg'
TEST_FAVICON = ASSETS_DIR / 'logo' / 'favicon' / 'favicon.ico'
