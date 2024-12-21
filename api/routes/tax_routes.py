from flask import Blueprint, request, jsonify
from api.utils.config import TAX_RATE, QUARTERLY_TAX_DATES
from api.utils.ai_utils import categorize_expense  # Import AI categorization
from datetime import datetime, timedelta
import logging
from api.utils.db_utils import get_db_connection  # Import database connection utility

# Configure Logging
logging.basicConfig(
    filename="tax_api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint Setup
tax_bp = Blueprint("tax_routes", __name__)

# Real-Time Tax Savings Endpoint
@tax_bp.route("/api/tax/savings", methods=["POST"])
def real_time_tax_savings():
    """
    Calculate real-time tax savings based on the provided expense amount.
    """
    try:
        data = request.json
        amount = data.get("amount")

        if not amount or float(amount) <= 0:
            return jsonify({"error": "Invalid or missing 'amount' parameter."}), 400

        savings = round(float(amount) * TAX_RATE, 2)
        return jsonify({"savings": savings}), 200
    except Exception as e:
        logging.error(f"Error calculating tax savings: {str(e)}")
        return jsonify({"error": "Failed to calculate tax savings."}), 500

# AI Deduction Suggestions Endpoint
@tax_bp.route("/api/tax/deductions", methods=["POST"])
def ai_deduction_suggestions():
    """
    Use AI to suggest tax-deductible expenses based on user input.
    """
    try:
        data = request.json
        expenses = data.get("expenses", [])

        if not expenses or not isinstance(expenses, list):
            return jsonify({"error": "Invalid or missing 'expenses' parameter."}), 400

        suggestions = []
        for expense in expenses:
            description = expense.get("description", "")
            category = categorize_expense(description)  # AI categorization
            if "business" in category.lower():  # Simple deduction flag
                suggestions.append({
                    "description": description,
                    "amount": expense.get("amount", 0),
                    "category": category
                })

        return jsonify({"suggestions": suggestions}), 200
    except Exception as e:
        logging.error(f"Error fetching deduction suggestions: {str(e)}")
        return jsonify({"error": "Failed to fetch AI deduction suggestions."}), 500

# Quarterly Tax Estimate Endpoint
@tax_bp.route("/api/tax/quarterly-estimate", methods=["POST"])
def quarterly_tax_estimate():
    """
    Calculate quarterly tax estimates based on income and expenses.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        quarter = data.get("quarter")
        year = data.get("year", datetime.now().year)

        if not all([user_id, quarter]):
            return jsonify({"error": "User ID and quarter are required."}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate quarterly income
        cursor.execute("""
            SELECT SUM(amount) FROM income 
            WHERE user_id = ? 
            AND QUARTER(date) = ? 
            AND YEAR(date) = ?
        """, (user_id, quarter, year))
        
        income = cursor.fetchone()[0] or 0

        # Calculate quarterly expenses
        cursor.execute("""
            SELECT SUM(amount) FROM expenses 
            WHERE user_id = ? 
            AND QUARTER(date) = ? 
            AND YEAR(date) = ?
        """, (user_id, quarter, year))
        
        expenses = cursor.fetchone()[0] or 0

        # Calculate estimated tax
        taxable_income = income - expenses
        estimated_tax = taxable_income * TAX_RATE
        
        due_date = QUARTERLY_TAX_DATES.get(str(quarter), "Unknown")

        return jsonify({
            "quarter": quarter,
            "year": year,
            "income": income,
            "expenses": expenses,
            "taxable_income": taxable_income,
            "estimated_tax": estimated_tax,
            "due_date": due_date
        }), 200
    except Exception as e:
        logging.error(f"Error calculating quarterly tax estimate: {str(e)}")
        return jsonify({"error": "Failed to calculate quarterly tax estimate."}), 500
