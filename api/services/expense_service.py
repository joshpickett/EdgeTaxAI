import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any
from utils.ai_utils import categorize_expense, analyze_expense_patterns
from utils.db_utils import get_db_connection
from utils.validators import validate_expense

class ExpenseService:
    def __init__(self):
        self.db = get_db_connection()

    def handle_expense(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle expense creation and categorization"""
        try:
            # Validate expense data
            validation_errors = validate_expense(data)
            if validation_errors:
                return {'error': validation_errors}, 400

            # Get AI categorization
            categorization = categorize_expense(data['description'])
            
            # Analyze patterns
            patterns = analyze_expense_patterns(data)
            
            # Combine data
            expense_data = {
                **data,
                'category': categorization['category'],
                'confidence_score': categorization['confidence'],
                'tax_deductible': categorization['tax_deductible'],
                'reasoning': categorization['reasoning'],
                'patterns': patterns
            }

            # Save to database
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO expenses 
                (description, amount, category, confidence_score, 
                tax_deductible, reasoning, source) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                expense_data['description'],
                expense_data['amount'],
                expense_data['category'],
                expense_data['confidence_score'],
                expense_data['tax_deductible'],
                expense_data['reasoning'],
                expense_data.get('source', 'manual')
            ))
            self.db.commit()

            return expense_data, 201

        except Exception as e:
            return {'error': str(e)}, 500
