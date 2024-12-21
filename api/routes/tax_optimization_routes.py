from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..utils.ai_utils import analyze_tax_context

tax_optimization_bp = Blueprint('tax_optimization', __name__)

@tax_optimization_bp.route("/optimize", methods=["POST"])
def optimize_tax_strategy():
    """
    Analyze expenses and suggest optimization strategies.
    This endpoint focuses purely on finding additional tax savings opportunities.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        expenses = data.get("expenses", [])
        
        if not all([user_id, expenses]):
            return jsonify({"error": "User ID and expenses are required"}), 400

        # Get enhanced tax context for each expense
        tax_contexts = [
            analyze_tax_context(exp.get('description', ''), exp.get('amount', 0))
            for exp in expenses
        ]

        return jsonify({
            "tax_contexts": tax_contexts,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500
