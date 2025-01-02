import pytest
from unittest.mock import MagicMock
from my_app.routes.mileage_routes import MileageService


@pytest.fixture
def mock_mileage_service(mocker):
    """
    Mock MileageService for mileage routes.
    """
    service = MagicMock(spec=MileageService)
    mocker.patch("my_app.routes.mileage_routes.mileage_service", service)
    yield service
