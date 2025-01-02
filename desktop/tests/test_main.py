import pytest
import streamlit as streamlit
from unittest.mock import Mock, patch
from ..main import main, check_auth


@pytest.fixture
def mock_streamlit():
    with patch("streamlit.title") as mock_title, patch(
        "streamlit.sidebar"
    ) as mock_sidebar, patch("streamlit.session_state") as mock_session:
        mock_session.user_id = 123
        yield {"title": mock_title, "sidebar": mock_sidebar, "session": mock_session}


def test_check_auth_logged_in(mock_streamlit):
    check_auth()
    # Should not raise any exceptions or redirect


def test_check_auth_not_logged_in():
    with patch("streamlit.session_state") as mock_session, patch(
        "streamlit.warning"
    ) as mock_warning, patch("streamlit.stop") as mock_stop:
        mock_session.user_id = None
        check_auth()
        mock_warning.assert_called_once()
        mock_stop.assert_called_once()


def test_main_navigation(mock_streamlit):
    with patch("streamlit.sidebar.radio") as mock_radio:
        mock_radio.return_value = "Dashboard"
        main()
        mock_streamlit["title"].assert_called_once_with("Welcome to EdgeTaxAI")


def test_logout_functionality(mock_streamlit):
    with patch("streamlit.sidebar.radio") as mock_radio, patch(
        "streamlit.success"
    ) as mock_success, patch("streamlit.experimental_rerun") as mock_rerun:
        mock_radio.return_value = "Logout"
        main()
        mock_success.assert_called_once_with("Logged out successfully!")
        mock_rerun.assert_called_once()


def test_gig_platform_integration():
    with patch("streamlit.experimental_get_query_params") as mock_params, patch(
        "streamlit.spinner"
    ) as mock_spinner:
        mock_params.return_value = {"code": ["test_code"], "platform": ["uber"]}
        main()
        mock_spinner.assert_called_with("Connecting to uber...")
