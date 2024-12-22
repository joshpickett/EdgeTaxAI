from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..utils.db_utils import get_db_connection
from ..utils.ai_utils import categorize_expense, analyze_expense_patterns, analyze_tax_context
from ..utils.validators import validate_expense
from ..utils.error_handler import handle_api_error
from ..utils.report_generator import ReportGenerator

expense_blueprint = Blueprint('expense', __name__)
report_generator = ReportGenerator()

@expense_blueprint.route('/expenses/summary', methods=['GET'])
def get_expense_summary():
    """Get expense summary with tax implications"""
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        summary = report_generator.generate_expense_summary(user_id, start_date, end_date)
        return jsonify(summary), 200
    except Exception as e:
        return handle_api_error(e)

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
                platform_trip_id, tax_deductible, tax_category,
                tax_context
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['description'],
            data['amount'],
            data['category'],
            data['platform_source'],
            data.get('platform_trip_id'),
            data['tax_deductible'],
            data.get('tax_category'),
            data.get('tax_context')
        ))
        connection.commit()
        cursor.close()
        connection.close()
        
        # Analyze tax implications
        tax_analysis = analyze_tax_context(data['description'], data['amount'])
        return jsonify({**data, 'tax_analysis': tax_analysis}), 201

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
