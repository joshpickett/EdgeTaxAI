from flask import Blueprint, request, jsonify
from api.utils.config import TAX_RATE, QUARTERLY_TAX_DATES
from datetime import datetime
from decimal import Decimal
import logging
from ..utils.analytics_helper import calculate_tax_savings, analyze_deductions
from ..utils.ai_utils import analyze_tax_context

"""
Core Tax Calculation Module

This module handles all core tax calculations and provides base functionality
for tax optimization features. It serves as the central source for tax-related
computations.
"""

# Enhanced tax brackets for more accurate calculations
TAX_BRACKETS = [
    (Decimal('0'), Decimal('11000'), Decimal('0.10')),
    (Decimal('11000'), Decimal('44725'), Decimal('0.12')),
    (Decimal('44725'), Decimal('95375'), Decimal('0.22')),
    (Decimal('95375'), Decimal('182100'), Decimal('0.24')),
    (Decimal('182100'), Decimal('231250'), Decimal('0.32')),
    (Decimal('231250'), Decimal('578125'), Decimal('0.35')),
    (Decimal('578125'), Decimal('inf'), Decimal('0.37'))
]

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
    This is the primary endpoint for basic tax savings calculations.
    
    For optimization suggestions, see: /api/tax-optimization/tax-savings
    """
    try:
        data = request.json
        amount = data.get("amount")
        user_id = data.get("user_id")

        if not amount or float(amount) <= 0:
            return jsonify({"error": "Invalid or missing 'amount' parameter."}), 400

        # Use centralized calculation function
        savings = calculate_tax_savings(float(amount), user_id)
        
        # Get tax context for enhanced analysis
        tax_context = analyze_tax_context(data.get('description', ''), amount)

        return jsonify({
            "savings": savings,
            "tax_context": tax_context,
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
        taxable_income = max(Decimal('0'), Decimal(income) - Decimal(expenses))
        estimated_tax = calculate_progressive_tax(taxable_income)
        
        due_date = QUARTERLY_TAX_DATES.get(str(quarter), "Unknown")

        return jsonify({
            "quarter": quarter,
            "year": year,
            "income": income,
            "expenses": expenses,
            "taxable_income": float(taxable_income),
            "estimated_tax": float(estimated_tax['total_tax']),
            "due_date": due_date
        }), 200
    except Exception as e:
        logging.error(f"Error calculating quarterly tax estimate: {str(e)}")
        return jsonify({"error": "Failed to calculate quarterly tax estimate."}), 500

def calculate_tax_bracket(income: float) -> tuple:
    """Calculate tax bracket and effective rate based on income"""
    for min_income, max_income, rate in TAX_BRACKETS:
        if min_income <= income <= max_income:
            return rate, f"${min_income:,} - ${max_income:,}"
    return TAX_BRACKETS[-1][2], f"Over ${TAX_BRACKETS[-1][0]:,}"

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
