from flask import Blueprint, request, jsonify, send_file
import logging
from datetime import datetime
from ..utils.db_utils import get_db_connection
import pandas as pd
import io

irs_bp = Blueprint('irs', __name__)

# Constants for IRS Forms
SCHEDULE_C_CATEGORIES = {
    'advertising': 'Line 8',
    'car_expenses': 'Line 9',
    'commissions': 'Line 10',
    'insurance': 'Line 15',
    'office_expense': 'Line 18',
    'supplies': 'Line 22',
    'travel': 'Line 24a',
    'meals': 'Line 24b',
    'utilities': 'Line 25',
    'other_expenses': 'Line 27a'
}

@irs_bp.route("/generate-schedule-c", methods=["POST"])
def generate_schedule_c():
    """Generate IRS Schedule C form data"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all expenses grouped by category
        cursor.execute("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ? AND strftime('%Y', date) = ?
            GROUP BY category
        """, (user_id, str(year)))

        expenses = cursor.fetchall()
        
        # Format for Schedule C
        schedule_c_data = {
            'gross_income': 0,  # Will be calculated from income table
            'expenses': {},
            'vehicle_expenses': 0,
            'total_expenses': 0
        }

        for category, amount in expenses:
            irs_line = SCHEDULE_C_CATEGORIES.get(category, 'other_expenses')
            schedule_c_data['expenses'][irs_line] = amount
            schedule_c_data['total_expenses'] += amount

        # Calculate net profit/loss
        schedule_c_data['net_profit'] = schedule_c_data['gross_income'] - schedule_c_data['total_expenses']

        return jsonify(schedule_c_data)

    except Exception as e:
        logging.error(f"Error generating Schedule C: {str(e)}")
        return jsonify({"error": "Failed to generate Schedule C"}), 500
