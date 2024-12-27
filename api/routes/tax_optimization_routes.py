import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from utils.shared_tax_service import TaxService
from utils.analytics_helper import analyze_optimization_opportunities
from decimal import Decimal

tax_optimization_bp = Blueprint('tax_optimization', __name__)
tax_service = TaxService()

@tax_optimization_bp.route("/tax/optimize", methods=["POST"])
def optimize_tax_strategy():
    """
    Analyze expenses and suggest optimization strategies.
    This endpoint focuses purely on finding additional tax savings opportunities.
    """
    try:
        data = request.json
        user_id = data.get("user_id")
        year = data.get('year', datetime.now().year)
        
        # Get comprehensive analysis
        optimization_results = analyze_optimization_opportunities(user_id, year)
        
        # Calculate potential savings
        potential_savings = tax_service.calculate_tax_savings(
            Decimal(str(optimization_results.get('potential_deductions', 0)))
        )

        return jsonify({
            "optimization_suggestions": optimization_results
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500

@tax_optimization_bp.route("/analyze-deductions", methods=["POST"])
def analyze_deductions():
    """Analyze potential deductions and optimization opportunities"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)

        # Get expenses and analyze deduction opportunities
        optimization_results = analyze_optimization_opportunities(user_id, year)
        
        potential_savings = tax_service.calculate_tax_savings(
            Decimal(str(optimization_results.get('potential_deductions', 0)))
        )

        return jsonify({
            "optimization_suggestions": optimization_results.get('suggestions', []),
            "potential_savings": potential_savings,
            "recommended_actions": optimization_results.get('recommendations', [])
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500

@tax_optimization_bp.route("/enhanced-analyze", methods=["POST"])
def enhanced_analyze():
    """Analyze expenses with AI-powered suggestions"""
    try:
        data = request.json
        user_id = data.get('user_id')
        quarter = data.get('quarter')
        expense_data = data.get('expense_data')

        if not all([user_id, quarter]):
            return jsonify({"error": "User ID and quarter are required"}), 400
            
        # Get AI-powered optimization suggestions
        optimization_results = tax_service.analyze_tax_context(expense_data)
        
        # Calculate potential savings
        potential_savings = tax_service.calculate_tax_savings(
            Decimal(str(optimization_results.get('potential_deductions', 0)))
        )

        return jsonify({
            "optimization_suggestions": optimization_results.get('suggestions', []),
            "potential_savings": potential_savings,
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(tax_optimization_bp)
    app.run(debug=True)
