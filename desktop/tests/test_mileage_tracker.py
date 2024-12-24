import pytest
from unittest.mock import Mock, patch
import streamlit as streamlit
from datetime import datetime
from desktop.mileage_tracker import mileage_tracker_page, track_new_trip, view_trip_history

@pytest.fixture
def mock_streamlit():
    with patch('desktop.mileage_tracker.streamlit') as mock_streamlit:
        yield mock_streamlit

@pytest.fixture
def mock_requests():
    with patch('desktop.mileage_tracker.requests') as mock_requests:
        yield mock_requests

@pytest.fixture
def sample_trip_data():
    return {
        'distance': 25.5,
        'tax_deduction': 14.75,
        'start': '123 Main St',
        'end': '456 Oak Ave',
        'purpose': 'Client Meeting'
    }

def test_track_new_trip_success(mock_streamlit, mock_requests, sample_trip_data):
    """Test successful trip tracking"""
    mock_requests.post.return_value.status_code = 200
    mock_requests.post.return_value.json.return_value = sample_trip_data
    
    # Mock user inputs
    mock_streamlit.text_input.side_effect = [
        sample_trip_data['start'],
        sample_trip_data['end'],
        sample_trip_data['purpose']
    ]
    mock_streamlit.date_input.return_value = datetime.now()
    mock_streamlit.checkbox.return_value = False
    mock_streamlit.button.return_value = True
    
    track_new_trip('http://test-api')
    
    mock_streamlit.success.assert_called_once()
    mock_requests.post.assert_called_once()

def test_track_new_trip_missing_fields(mock_streamlit, mock_requests):
    """Test trip tracking with missing fields"""
    mock_streamlit.text_input.side_effect = ['', '', '']
    mock_streamlit.button.return_value = True
    
    track_new_trip('http://test-api')
    
    mock_streamlit.error.assert_called_with("All fields are required.")
    mock_requests.post.assert_not_called()

def test_track_new_trip_api_error(mock_streamlit, mock_requests):
    """Test trip tracking with API error"""
    mock_requests.post.return_value.status_code = 400
    mock_requests.post.return_value.json.return_value = {'error': 'API Error'}
    
    mock_streamlit.text_input.side_effect = ['Start', 'End', 'Purpose']
    mock_streamlit.date_input.return_value = datetime.now()
    mock_streamlit.button.return_value = True
    
    track_new_trip('http://test-api')
    
    mock_streamlit.error.assert_called()

def test_view_trip_history_success(mock_streamlit, mock_requests):
    """Test successful trip history viewing"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = [
        {
            'date': '2023-01-01',
            'start': 'Start Location',
            'end': 'End Location',
            'distance': 20.0,
            'purpose': 'Business',
            'tax_deduction': 11.60
        }
    ]
    
    view_trip_history('http://test-api')
    
    mock_streamlit.table.assert_called_once()
    mock_requests.get.assert_called_once()

def test_view_trip_history_empty(mock_streamlit, mock_requests):
    """Test viewing empty trip history"""
    mock_requests.get.return_value.status_code = 200
    mock_requests.get.return_value.json.return_value = []
    
    view_trip_history('http://test-api')
    
    mock_streamlit.info.assert_called_with("No trips recorded yet.")

def test_view_trip_history_error(mock_streamlit, mock_requests):
    """Test trip history viewing with error"""
    mock_requests.get.side_effect = Exception("API Error")
    
    view_trip_history('http://test-api')
    
    mock_streamlit.error.assert_called()

def test_recurring_trip_setup(mock_streamlit, mock_requests, sample_trip_data):
    """Test setting up recurring trip"""
    mock_requests.post.return_value.status_code = 200
    mock_requests.post.return_value.json.return_value = sample_trip_data
    
    mock_streamlit.text_input.side_effect = [
        sample_trip_data['start'],
        sample_trip_data['end'],
        sample_trip_data['purpose']
    ]
    mock_streamlit.date_input.return_value = datetime.now()
    mock_streamlit.checkbox.return_value = True
    mock_streamlit.selectbox.return_value = "Weekly"
    mock_streamlit.button.return_value = True
    
    track_new_trip('http://test-api')
    
    mock_streamlit.success.assert_called()
    assert "recurring" in mock_requests.post.call_args[1]['json']

def test_mileage_tracker_page_tabs(mock_streamlit):
    """Test mileage tracker page tabs"""
    mock_tabs = [Mock(), Mock()]
    mock_streamlit.tabs.return_value = mock_tabs
    
    mileage_tracker_page('http://test-api')
    
    mock_streamlit.tabs.assert_called_once_with(["Track New Trip", "View History"])
