import os
import sys
from api.setup_path import setup_python_path

setup_python_path(__file__)

from flask import Blueprint, request, jsonify, send_file
import logging
from datetime import datetime
from api.utils.db_utils import get_db_connection
from api.utils.tax_calculator import TaxCalculator
from api.utils.income_tax_utils import IncomeTaxCalculator
from api.utils.irs_compliance import IRSCompliance
from api.utils.session_manager import SessionManager
from api.utils.token_manager import TokenManager

# Initialize managers
session_manager = SessionManager()
token_manager = TokenManager()

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
        user_id = data.get("user_id")
        quarter = data.get("quarter")
        year = data.get("year", datetime.now().year)

        if not all([user_id, quarter]):
            return jsonify({"error": "User ID and quarter required"}), 400

        # Get quarterly calculations from the utility
        quarterly_data = IncomeTaxCalculator.calculate_quarterly_amounts(
            user_id, quarter, year
        )

        # Calculate estimated tax
        estimated_tax = irs_calculator.calculate_self_employment_tax(
            quarterly_data["net_income"]
        )["tax_amount"]

        return jsonify(
            {
                **quarterly_data,
                "estimated_tax": estimated_tax,
            }
        )

    except Exception as e:
        logging.error(f"Error generating quarterly estimate: {str(e)}")
        return jsonify({"error": "Failed to generate quarterly estimate"}), 500


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(irs_bp)
    app.run(debug=True)
