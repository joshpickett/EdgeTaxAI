from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..utils.analytics_helper import analyze_optimization_opportunities, analyze_deductions

tax_optimization_bp = Blueprint('tax_optimization', __name__)

@tax_optimization_bp.route("/tax-savings", methods=["POST"])
def calculate_tax_savings():
    """
    Calculate potential tax savings based on expense optimization opportunities.
    Uses AI analysis to identify additional deduction possibilities.
    
    See also: /api/tax/savings for core tax savings calculations
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        year = data.get("year", datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Use analytics helper for optimization analysis
        optimization_results = analyze_optimization_opportunities(user_id, year)

        return jsonify({
            "optimization_suggestions": optimization_results
        }), 200
    except Exception as e:
        logging.error(f"Error calculating tax savings: {str(e)}")
        return jsonify({"error": "Failed to calculate tax savings"}), 500

@tax_optimization_bp.route("/deduction-analysis", methods=["POST"])
def analyze_deductions():
    """
    Analyze expenses for potential tax deductions using AI.
    
    This endpoint focuses on finding optimization opportunities and
    suggesting potential deductions that might have been missed.
    
    See also: /api/tax/deductions for standard deduction calculations
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        # Use enhanced deduction analysis from analytics helper
        deduction_analysis = analyze_deductions(user_id)
        
        # Add optimization suggestions
        optimization_suggestions = analyze_optimization_opportunities(user_id)

        return jsonify({
            "deduction_analysis": deduction_analysis,
            "optimization_suggestions": optimization_suggestions,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500
