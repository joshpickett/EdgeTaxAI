import pytest
from unittest.mock import MagicMock
from my_app.routes.gig_routes import GigService


@pytest.fixture
def mock_gig_service(mocker):
    """
    Mock GigService for gig routes.
    """
    service = MagicMock(spec=GigService)
    mocker.patch("my_app.routes.gig_routes.gig_service", service)
    yield service
