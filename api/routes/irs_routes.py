from flask import Blueprint, request, jsonify, send_file
import logging
from datetime import datetime
from ..utils.db_utils import get_db_connection
from ..utils.error_handler import handle_api_error
import pandas as pd
import io
import os

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

@irs_bp.route("/year-end-summary", methods=["POST"])
def generate_year_end_summary():
    """Generate year-end tax summary"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total income
        cursor.execute("""
            SELECT SUM(amount) as total_income
            FROM income
            WHERE user_id = ? AND strftime('%Y', date) = ?
        """, (user_id, str(year)))
        
        total_income = cursor.fetchone()[0] or 0

        # Get expenses by quarter
        cursor.execute("""
            SELECT 
                strftime('%m', date) as month,
                category,
                SUM(amount) as total
            FROM expenses
            WHERE user_id = ? AND strftime('%Y', date) = ?
            GROUP BY month, category
            ORDER BY month
        """, (user_id, str(year)))

        quarterly_expenses = {
            'Q1': {'total': 0, 'categories': {}},
            'Q2': {'total': 0, 'categories': {}},
            'Q3': {'total': 0, 'categories': {}},
            'Q4': {'total': 0, 'categories': {}}
        }

        for month, category, amount in cursor.fetchall():
            quarter = (int(month) - 1) // 3 + 1
            q_key = f'Q{quarter}'
            quarterly_expenses[q_key]['total'] += amount
            if category not in quarterly_expenses[q_key]['categories']:
                quarterly_expenses[q_key]['categories'][category] = 0
            quarterly_expenses[q_key]['categories'][category] += amount

        # Calculate estimated taxes
        tax_rate = 0.25  # Default tax rate
        estimated_tax = total_income * tax_rate
        quarterly_tax = estimated_tax / 4

        summary = {
            'year': year,
            'total_income': total_income,
            'quarterly_expenses': quarterly_expenses,
            'estimated_tax': estimated_tax,
            'quarterly_tax_payments': quarterly_tax,
            'tax_rate': tax_rate
        }

        return jsonify(summary)

    except Exception as e:
        logging.error(f"Error generating year-end summary: {str(e)}")
        return jsonify({"error": "Failed to generate year-end summary"}), 500

@irs_bp.route("/export-tax-data", methods=["POST"])
def export_tax_data():
    """Export tax data in IRS-compatible format"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        format_type = data.get('format', 'csv')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all relevant tax data
        cursor.execute("""
            SELECT 
                date,
                category,
                description,
                amount
            FROM expenses
            WHERE user_id = ? AND strftime('%Y', date) = ?
            ORDER BY date
        """, (user_id, str(year)))

        expenses = cursor.fetchall()
        
        # Create DataFrame
        df = pd.DataFrame(expenses, columns=['Date', 'Category', 'Description', 'Amount'])
        
        if format_type == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'tax_data_{year}.csv'
            )
        else:
            # Format for other IRS-compatible formats
            return jsonify({"error": "Format not supported"}), 400

    except Exception as e:
        logging.error(f"Error exporting tax data: {str(e)}")
        return jsonify({"error": "Failed to export tax data"}), 500
