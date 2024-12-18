from flask import Blueprint, request, jsonify, send_file
from io import BytesIO
import csv
import pandas as pd
from utils.db_utils import get_user_expenses  # Utility to fetch expenses from DB
from config import REPORTS_DIRECTORY  # Directory to save reports
import logging

# Configure Logging
logging.basicConfig(
    filename="reports_routes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint Setup
reports_bp = Blueprint("reports_routes", __name__)

# 1. Generate Reports for a User
@reports_bp.route("/api/reports/<int:user_id>", methods=["GET"])
def generate_reports(user_id):
    """
    Generates IRS-ready PDF and CSV reports for a user's expenses.
    """
    try:
        # Fetch expense data
        expenses = get_user_expenses(user_id)
        if not expenses:
            return jsonify({"error": "No expenses found for the user."}), 404

        # Convert expenses to DataFrame
        df = pd.DataFrame(expenses)

        # Generate CSV report
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Generate PDF (simple conversion)
        pdf_buffer = BytesIO()
        df.to_string(pdf_buffer)
        pdf_buffer.seek(0)

        # Return the reports
        return jsonify({
            "pdf": pdf_buffer.getvalue().decode("utf-8"),
            "csv": csv_buffer.getvalue().decode("utf-8")
        })
    except Exception as e:
        logging.error(f"Error generating reports: {str(e)}")
        return jsonify({"error": "Failed to generate reports."}), 500


# 2. Generate Custom Reports
@reports_bp.route("/api/reports/custom/<int:user_id>", methods=["POST"])
def generate_custom_reports(user_id):
    """
    Generates custom reports based on filters like date range or category.
    """
    try:
        filters = request.json
        start_date = filters.get("start_date")
        end_date = filters.get("end_date")
        category = filters.get("category")

        # Fetch filtered expenses
        expenses = get_user_expenses(user_id, start_date, end_date, category)
        if not expenses:
            return jsonify({"error": "No expenses match the given filters."}), 404

        # Convert expenses to CSV
        df = pd.DataFrame(expenses)
        csv_buffer = BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        return send_file(csv_buffer, mimetype="text/csv", as_attachment=True, download_name="custom_report.csv")
    except Exception as e:
        logging.error(f"Error generating custom report: {str(e)}")
        return jsonify({"error": "Failed to generate custom report."}), 500
