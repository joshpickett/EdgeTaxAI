from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from ..services.expense_service import ExpenseService
from ..utils.ai_utils import categorize_expense, analyze_expense_patterns
from ..utils.validators import validate_expense
from ..utils.error_handler import handle_api_error
from ..utils.report_generator import ReportGenerator

expense_blueprint = Blueprint('expense', __name__)
report_generator = ReportGenerator()
expense_service = ExpenseService()

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
    return expense_service.handle_expense(data)
