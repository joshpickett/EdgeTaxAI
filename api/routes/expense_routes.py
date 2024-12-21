from flask import Blueprint, request, jsonify
from datetime import datetime
from ..utils.db_utils import get_db_connection
from ..utils.ai_utils import categorize_expense, analyze_expense_patterns
from ..utils.validators import validate_expense
from ..utils.error_handler import handle_api_error

expense_blueprint = Blueprint('expense', __name__)

@expense_blueprint.route('/expenses', methods=['POST'])
def create_expense():
    data = request.json
    description = data.get('description', '')
    
    # Categorize expense
    categorization = categorize_expense(description)
    data['category'] = categorization['category']
    data['confidence_score'] = categorization['confidence']
    data['tax_deductible'] = categorization['tax_deductible']
    data['reasoning'] = categorization['reasoning']
    data['source'] = categorization['source']

    # Validate expense data
    validation_errors = validate_expense(data)
    if validation_errors:
        return handle_api_error(validation_errors)

    # Save to database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO expenses (description, category, confidence_score, tax_deductible, reasoning, source) VALUES (?, ?, ?, ?, ?, ?)',
                   (description, data['category'], data['confidence_score'], data['tax_deductible'], data['reasoning'], data['source']))
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify(data), 201
