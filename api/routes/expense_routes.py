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
    
    # Handle gig platform expenses
    if data.get('platform_source'):
        data['category'] = 'gig_platform'
        data['tax_deductible'] = True
        
    # Categorize expense
    categorization = categorize_expense(description)
    
    # Store expense with platform data if available
    if data.get('platform_source'):
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO expenses (
                description, amount, category, platform_source, 
                platform_trip_id, tax_deductible
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['description'],
            data['amount'],
            data['category'],
            data['platform_source'],
            data.get('platform_trip_id'),
            data['tax_deductible']
        ))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(data), 201

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
