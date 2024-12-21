from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..utils.analytics_helper import analyze_optimization_opportunities

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
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Use analytics helper for optimization analysis
        optimization_results = analyze_optimization_opportunities(user_id)

        return jsonify({
            "optimization_suggestions": optimization_results
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500
