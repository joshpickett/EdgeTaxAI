from flask import Blueprint, request, jsonify, send_file
import logging
from datetime import datetime
from ..utils.db_utils import get_db_connection
from ..utils.tax_calculator import TaxCalculator
from ..utils.irs_compliance import IRSCompliance

irs_calculator = TaxCalculator()
irs_compliance = IRSCompliance()

# Initialize Blueprint
irs_bp = Blueprint("irs", __name__, url_prefix="/api/irs")

@irs_bp.route("/generate-schedule-c", methods=["POST"])
def generate_schedule_c():
    """Generate IRS Schedule C form data"""
    try:
        return irs_calculator.generate_schedule_c(request.json)
    except Exception as e:
        logging.error(f"Error generating Schedule C: {str(e)}")
        return jsonify({"error": "Failed to generate Schedule C"}), 500

@irs_bp.route("/quarterly-estimate", methods=["POST"])
def generate_quarterly_estimate():
    """Generate quarterly tax estimate"""
    try:
        data = request.json
        user_id = data.get('user_id')
        quarter = data.get('quarter')
        year = data.get('year', datetime.now().year)
        
        if not all([user_id, quarter]):
            return jsonify({"error": "User ID and quarter required"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate quarterly income and expenses
        quarter_start = f"{year}-{(quarter-1)*3+1:02d}-01"
        quarter_end = f"{year}-{quarter*3:02d}-31"
        
        cursor.execute("""
            SELECT SUM(amount) as total_income
            FROM income
            WHERE user_id = ? 
            AND date BETWEEN ? AND ?
        """, (user_id, quarter_start, quarter_end))
        
        total_income = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT SUM(amount) as total_expenses
            FROM expenses
            WHERE user_id = ?
            AND date BETWEEN ? AND ?
        """, (user_id, quarter_start, quarter_end))
        
        total_expenses = cursor.fetchone()[0] or 0
        
        # Calculate estimated tax
        net_income = total_income - total_expenses
        estimated_tax = irs_calculator.calculate_self_employment_tax(net_income)['tax_amount']
        
        def get_quarter_due_date(quarter, year):
            """Calculate the due date for quarterly taxes"""
            due_dates = {
                1: f"{year}-04-15",  # Q1 due April 15
                2: f"{year}-06-15",  # Q2 due June 15
                3: f"{year}-09-15",  # Q3 due September 15
                4: f"{year+1}-01-15"  # Q4 due January 15 of next year
            }
            return due_dates.get(quarter)

        return jsonify({
            'quarter': quarter,
            'year': year,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'estimated_tax': estimated_tax,
            'due_date': get_quarter_due_date(quarter, year)
        })
        
    except Exception as e:
        logging.error(f"Error generating quarterly estimate: {str(e)}")
        return jsonify({"error": "Failed to generate quarterly estimate"}), 500
