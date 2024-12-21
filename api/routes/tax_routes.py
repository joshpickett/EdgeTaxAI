from flask import Blueprint, request, jsonify
from datetime import datetime
from decimal import Decimal
import logging
from ..utils.analytics_helper import calculate_tax_savings
from ..utils.tax_calculator import TaxCalculator
from ..utils.db_utils import get_db_connection

"""
Core Tax Calculation Module - Centralized tax calculation functionality
Handles all basic tax calculations and estimates
"""

# Configure Logging
logging.basicConfig(
    filename="tax_api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint Setup
tax_bp = Blueprint("tax_routes", __name__)

@tax_bp.route("/api/tax/estimate-quarterly", methods=["POST"])
def estimate_quarterly_tax():
    """Calculate quarterly estimated tax payments"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        quarter = data.get('quarter')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get income and expenses for the quarter
        cursor.execute("""
            SELECT SUM(amount) as total_income
            FROM income
            WHERE user_id = ? AND strftime('%Y-%m', date) BETWEEN ? AND ?
        """, (user_id, f"{year}-{(quarter-1)*3+1:02d}", f"{year}-{quarter*3:02d}"))
        
        income = cursor.fetchone()[0] or 0
        
        calculator = TaxCalculator()
        estimate = calculator.calculate_quarterly_tax(Decimal(str(income)), Decimal('0'))
        
        return jsonify(estimate), 200
    except Exception as e:
        logging.error(f"Error calculating quarterly estimate: {e}")
        return jsonify({"error": "Failed to calculate quarterly estimate"}), 500

# Real-Time Tax Savings Endpoint
@tax_bp.route("/api/tax/savings", methods=["POST"])
def real_time_tax_savings():
    """
    Calculate real-time tax savings based on the provided expense amount.
    This is the primary endpoint for basic tax savings calculations.
    
    For optimization suggestions, see: /api/tax-optimization/tax-savings
    """
    try:
        data = request.json
        amount = data.get("amount")
        user_id = data.get("user_id")

        if not amount or float(amount) <= 0:
            return jsonify({"error": "Invalid amount"}), 400

        # Use centralized calculation
        calculator = TaxCalculator()
        savings = calculator.calculate_tax_savings(Decimal(str(amount)))

        return jsonify({
            "savings": savings,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Error calculating tax savings: {str(e)}")
        return jsonify({"error": "Failed to calculate tax savings."}), 500

# AI Deduction Suggestions Endpoint
@tax_bp.route("/api/tax/deductions", methods=["POST"])
def ai_deduction_suggestions():
    """
    Calculate standard deductions based on expense data.
    Uses basic categorization for common deduction types.
    
    For advanced deduction analysis and optimization, 
    see: /api/tax-optimization/deduction-analysis
    """
    try:
        data = request.json
        expenses = data.get("expenses", [])

        if not expenses or not isinstance(expenses, list):
            return jsonify({"error": "Invalid or missing 'expenses' parameter."}), 400

        # Use centralized deduction analysis
        deduction_analysis = analyze_deductions(expenses)
        
        # Add confidence scores and AI insights
        enhanced_suggestions = [{
            **suggestion,
            "confidence_score": suggestion.get("confidence", 0),
            "ai_insights": suggestion.get("reasoning", "")
        } for suggestion in deduction_analysis]

        return jsonify({"suggestions": enhanced_suggestions}), 200
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

        income = Decimal(str(data.get("income", 0)))
        expenses = Decimal(str(data.get("expenses", 0)))

        calculator = TaxCalculator()
        tax_result = calculator.calculate_quarterly_tax(income, expenses)

        return jsonify({
            "quarter": quarter,
            "year": year,
            "income": float(income),
            "expenses": float(expenses),
            "quarterly_tax": tax_result['quarterly_amount'],
            "annual_tax": tax_result['annual_tax'],
            "effective_rate": tax_result['effective_rate']
        }), 200
    except Exception as e:
        logging.error(f"Error calculating quarterly tax estimate: {str(e)}")
        return jsonify({"error": "Failed to calculate quarterly tax estimate."}), 500

def calculate_tax_bracket(income: float) -> tuple:
    """Calculate tax bracket and effective rate based on income"""
    for min_income, max_income, rate in TaxCalculator.TAX_BRACKETS:
        if min_income <= income <= max_income:
            return rate, f"${min_income:,} - ${max_income:,}"
    return TaxCalculator.TAX_BRACKETS[-1][2], f"Over ${TaxCalculator.TAX_BRACKETS[-1][0]:,}"

@tax_bp.route("/calculate-effective-rate", methods=["POST"])
def calculate_effective_rate():
    """Calculate effective tax rate based on income and deductions"""
    try:
        data = request.json
        gross_income = Decimal(data.get("gross_income", 0))
        deductions = Decimal(data.get("deductions", 0))
        
        taxable_income = max(Decimal('0'), gross_income - deductions)
        tax_rate, bracket = calculate_tax_bracket(taxable_income)
        
        return jsonify({
            "taxable_income": float(taxable_income),
            "tax_bracket": bracket,
            "tax_rate": float(tax_rate),
            "estimated_tax": float(taxable_income * tax_rate)
        })
    except Exception as e:
        logging.error(f"Error calculating effective tax rate: {str(e)}")
        return jsonify({"error": "Failed to calculate effective tax rate"}), 500
