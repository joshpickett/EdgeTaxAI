import pytest
from unittest.mock import Mock, patch
from ..utils.ai_utils import (
    categorize_expense,
    analyze_expense_patterns,
    analyze_tax_context,
    update_learning_system,
    enhanced_fallback_categorization
)

class TestAIUtils:
    @pytest.fixture
    def mock_openai(self):
        with patch('openai.OpenAI') as mock:
            yield mock

    @pytest.fixture
    def mock_database(self):
        with patch('sqlite3.connect') as mock:
            yield mock

    def test_categorize_expense_success(self, mock_openai):
        mock_openai.return_value.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Office Supplies|0.95|Receipt contains office items|true"))
        ]

        result = categorize_expense("Office paper and supplies from Staples")
        
        assert result['category'] == 'Office Supplies'
        assert result['confidence'] > 0.9
        assert 'reasoning' in result
        assert 'tax_deductible' in result

    def test_analyze_expense_patterns(self):
        expenses = [
            {'description': 'Uber ride', 'amount': 25.0, 'date': '2023-01-01'},
            {'description': 'Office supplies', 'amount': 50.0, 'date': '2023-01-02'},
        ]
        
        patterns = analyze_expense_patterns(expenses)
        
        assert 'frequency' in patterns
        assert 'amount' in patterns
        assert 'time' in patterns
        assert 'location' in patterns

    def test_analyze_tax_context_success(self):
        result = analyze_tax_context("Office supplies purchase", 100.0)
        
        assert result['context'] in ['business', 'personal', 'mixed']
        assert 'confidence' in result
        assert 'suggested_category' in result
        assert 'deductible_amount' in result

    def test_update_learning_system(self, mock_database):
        mock_cursor = Mock()
        mock_database.return_value.cursor.return_value = mock_cursor
        
        expense_data = {
            'description': 'Office supplies',
            'amount': 100.0,
            'category': 'office_expense'
        }
        
        update_learning_system(expense_data, 'office_supplies')
        
        mock_cursor.execute.assert_called_once()
        mock_database.return_value.commit.assert_called_once()

    def test_enhanced_fallback_categorization(self):
        test_cases = [
            ('Uber ride to airport', 'transport'),
            ('Lunch meeting with client', 'meals'),
            ('New printer for office', 'office_supplies'),
            ('Unknown expense', 'other')
        ]
        
        for description, expected_category in test_cases:
            result = enhanced_fallback_categorization(description)
            assert result['category'] == expected_category
            assert 'confidence' in result
            assert 'is_business' in result

    def test_pattern_recognition(self):
        expenses = [
            {'description': 'Coffee meeting', 'amount': 15.0, 'date': '2023-01-01 09:00:00'},
            {'description': 'Lunch with client', 'amount': 45.0, 'date': '2023-01-01 13:00:00'},
        ]
        
        patterns = analyze_expense_patterns(expenses)
        
        assert 'time_based' in patterns
        assert patterns['time_based']['morning']['categories']['meals'] > 0
        assert patterns['time_based']['afternoon']['categories']['meals'] > 0

    def test_location_pattern_analysis(self):
        expenses = [
            {'description': 'Starbucks NYC', 'amount': 5.0},
            {'description': 'Starbucks NYC', 'amount': 5.0},
        ]
        
        patterns = analyze_expense_patterns(expenses)
        
        assert 'location' in patterns
        assert 'NYC' in str(patterns['location'])
        assert patterns['location']['NYC']['count'] == 2

    def test_vendor_pattern_analysis(self):
        expenses = [
            {'description': 'Amazon.com Office Supplies', 'amount': 50.0},
            {'description': 'Amazon.com Electronics', 'amount': 100.0},
        ]
        
        patterns = analyze_expense_patterns(expenses)
        
        assert 'vendor' in patterns
        assert 'Amazon' in str(patterns['vendor'])
        assert patterns['vendor']['Amazon']['count'] == 2

    @patch('api.utils.ai_utils.calculate_correction_confidence')
    def test_learning_system_confidence(self, mock_calculate_correction_confidence):
        mock_calculate_correction_confidence.return_value = 0.95
        
        expense_data = {
            'description': 'Office supplies',
            'amount': 100.0,
            'category': 'office_expense'
        }
        
        update_learning_system(expense_data, 'office_supplies')
        
        mock_calculate_correction_confidence.assert_called_once()
