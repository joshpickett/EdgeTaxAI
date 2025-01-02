import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from desktop.plaid_integration import plaid_integration_page


@pytest.fixture
def mock_streamlit():
    with patch("desktop.plaid_integration.streamlit") as mock_streamlit:
        yield mock_streamlit


@pytest.fixture
def mock_requests():
    with patch("desktop.plaid_integration.requests") as mock_requests:
        yield mock_requests


def test_plaid_integration_page_title(mock_streamlit):
    """Test page title and header rendering"""
    plaid_integration_page()

    mock_streamlit.title.assert_called_once_with("Plaid Integration")
    mock_streamlit.markdown.assert_called_once_with(
        "#### Connect your bank accounts securely."
    )


def test_plaid_integration_page_icon(mock_streamlit):
    """Test icon rendering"""
    plaid_integration_page()

    mock_streamlit.image.assert_called_once()
    assert "edgetaxai-icon-color.svg" in str(mock_streamlit.image.call_args[0][0])
