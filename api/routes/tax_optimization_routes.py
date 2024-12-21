from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..utils.ai_utils import analyze_tax_data, generate_tax_insights
from ..utils.db_utils import get_db_connection

tax_optimization_bp = Blueprint('tax_optimization', __name__)

@tax_optimization_bp.route("/tax-savings", methods=["POST"])
def calculate_tax_savings():
    """Calculate potential tax savings based on expenses."""
    try:
        data = request.json
        user_id = data.get("user_id")
        year = data.get("year", datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calculate total expenses
        cursor.execute(
            """
            SELECT SUM(amount) as total_expenses
            FROM expenses 
            WHERE user_id = ? AND YEAR(date) = ?
            """,
            (user_id, year)
        )
        total_expenses = cursor.fetchone()[0] or 0
        
        # Calculate estimated savings (25% tax rate)
        estimated_savings = total_expenses * 0.25
        
        return jsonify({
            "total_expenses": total_expenses,
            "estimated_savings": estimated_savings,
            "year": year
        }), 200
    except Exception as e:
        logging.error(f"Error calculating tax savings: {str(e)}")
        return jsonify({"error": "Failed to calculate tax savings"}), 500

# ...rest of the code...

@tax_optimization_bp.route("/deduction-analysis", methods=["POST"])
def analyze_deductions():
    """Analyze expenses for potential tax deductions."""
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch expenses
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
            (user_id,)
        )
        expenses = cursor.fetchall()

        # Generate AI analysis
        analysis = analyze_tax_data(expenses)

        return jsonify({
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Error analyzing deductions: {str(e)}")
        return jsonify({"error": "Failed to analyze deductions"}), 500
