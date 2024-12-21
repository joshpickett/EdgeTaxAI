import pytest
from datetime import datetime
from api.utils.ai_utils import categorize_expense, analyze_expense_patterns

class TestCategorization:
    def test_basic_categorization(self):
        description = "Lunch meeting with client"
        result = categorize_expense(description)
        assert result['category'] in ['Food', 'Meals']
        assert 'confidence' in result
        assert 'tax_deductible' in result

...rest of the code...
