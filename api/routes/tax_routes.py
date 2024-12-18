from flask import Blueprint, request, jsonify
from api.utils.config import TAX_RATE  # Import centralized tax rate
from api.utils.ai_utils import categorize_expense  # Import AI categorization
import logging

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
