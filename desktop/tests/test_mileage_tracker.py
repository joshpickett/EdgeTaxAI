import pytest
import streamlit as streamlit
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from ..mileage_tracker import mileage_tracker_page, track_new_trip, view_trip_history

@pytest.fixture
def mock_mileage_service():
    return Mock()

@pytest.fixture
def mock_streamlit():
    with patch('streamlit.title') as mock_title, \
         patch('streamlit.image') as mock_image, \
         patch('streamlit.markdown') as mock_markdown, \
         patch('streamlit.tabs') as mock_tabs:
        yield {
            'title': mock_title,
            'image': mock_image,
            'markdown': mock_markdown,
            'tabs': mock_tabs
        }

def test_mileage_tracker_page_initialization(mock_streamlit):
    mileage_tracker_page("http://test-api")
    mock_streamlit['title'].assert_called_once_with("Mileage Tracker")
    mock_streamlit['markdown'].assert_called_with("#### Track your business mileage for tax deductions")

def test_track_new_trip_success(mock_mileage_service):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.date_input') as mock_date, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success:
        
        mock_input.side_effect = ["123 Start St", "456 End St", "Business Meeting"]
        mock_date.return_value = datetime.now()
        mock_button.return_value = True
        
        mock_mileage_service.calculateMileage.return_value = {
            'status_code': 200,
            'data': {
                'distance': 10.5,
                'tax_deduction': 5.25
            }
        }
        
        track_new_trip(mock_mileage_service)
        mock_success.assert_called_once()
        mock_mileage_service.calculateMileage.assert_called_once()

def test_track_new_trip_validation_error(mock_mileage_service):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.error') as mock_error:
        
        mock_input.side_effect = ["", "", ""]
        mock_button.return_value = True
        
        track_new_trip(mock_mileage_service)
        mock_error.assert_called_with("All fields are required.")
        mock_mileage_service.calculateMileage.assert_not_called()

def test_view_trip_history_success(mock_mileage_service):
    mock_trips = {
        'status_code': 200,
        'data': [
            {
                'date': '2023-01-01',
                'start': '123 Start St',
                'end': '456 End St',
                'distance': 10.5,
                'purpose': 'Business Meeting',
                'tax_deduction': 5.25
            }
        ]
    }
    
    mock_mileage_service.getMileageHistory.return_value = mock_trips
    
    with patch('streamlit.metric') as mock_metric:
        view_trip_history(mock_mileage_service)
        assert mock_metric.call_count == 2

def test_view_trip_history_error(mock_mileage_service):
    mock_mileage_service.getMileageHistory.side_effect = Exception("API Error")
    
    with patch('streamlit.error') as mock_error:
        view_trip_history(mock_mileage_service)
        mock_error.assert_called_with("Error fetching trip history: API Error")

def test_recurring_trip_functionality(mock_mileage_service):
    with patch('streamlit.text_input') as mock_input, \
         patch('streamlit.date_input') as mock_date, \
         patch('streamlit.checkbox') as mock_checkbox, \
         patch('streamlit.selectbox') as mock_selectbox, \
         patch('streamlit.button') as mock_button:
        
        mock_input.side_effect = ["123 Start St", "456 End St", "Daily Commute"]
        mock_date.return_value = datetime.now()
        mock_checkbox.return_value = True
        mock_selectbox.return_value = "Daily"
        mock_button.return_value = True
        
        mock_mileage_service.calculateMileage.return_value = {
            'status_code': 200,
            'data': {
                'distance': 10.5,
                'tax_deduction': 5.25
            }
        }
        
        track_new_trip(mock_mileage_service)
        
        expected_payload = {
            'start': '123 Start St',
            'end': '456 End St',
            'purpose': 'Daily Commute',
            'recurring': True,
            'frequency': 'Daily'
        }
        
        mock_mileage_service.calculateMileage.assert_called_once()
        actual_payload = mock_mileage_service.calculateMileage.call_args[0][0]
        assert actual_payload['recurring'] == expected_payload['recurring']
        assert actual_payload['frequency'] == expected_payload['frequency']
