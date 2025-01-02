import os
import sys
from api.setup_path import setup_python_path

setup_python_path(__file__)

from flask import Blueprint, request, jsonify
from shared.types.tax import TaxCalculationResult, TaxDeduction
from api.schemas.tax_schemas import (
    QuarterlyTaxSchema,
    TaxSavingsSchema,
    DeductionAnalysisSchema,
    TaxDocumentSchema,
)
from api.config.tax_config import TAX_CONFIG
from api.services.tax_service import TaxService
from api.services.tax_optimization_service import TaxOptimizationService
from api.services.export_service import ExportService
from api.utils.error_handler import handle_api_error
from api.utils.rate_limit import rate_limit
from api.utils.cache_utils import cache_response
from api.utils.audit_trail import AuditLogger

# Initialize services
tax_service = TaxService()
audit_logger = AuditLogger()
export_service = ExportService()

tax_bp = Blueprint("tax_routes", __name__)


@tax_bp.route("/api/tax/estimate-quarterly", methods=["POST"])
@rate_limit(requests_per_minute=TAX_CONFIG["RATE_LIMITS"]["tax_calculation"])
@cache_response(timeout=TAX_CONFIG["CACHE_SETTINGS"]["tax_calculation"])
def estimate_quarterly_tax():
    """Calculate quarterly estimated tax payments"""
    try:
        schema = QuarterlyTaxSchema()
        data = schema.load(request.json)
        return tax_service.estimate_quarterly_taxes(data)
    except Exception as e:
        return handle_api_error(e)


@tax_bp.route("/api/tax/savings", methods=["POST"])
@rate_limit(requests_per_minute=TAX_CONFIG["RATE_LIMITS"]["tax_calculation"])
@cache_response(timeout=TAX_CONFIG["CACHE_SETTINGS"]["tax_calculation"])
def real_time_tax_savings():
    """Calculate real-time tax savings based on expense amount"""
    try:
        schema = TaxSavingsSchema()
        data = schema.load(request.json)
        result = tax_service.calculate_tax_savings(data["amount"])
        return jsonify(result), 200
    except Exception as e:
        return handle_api_error(e)


# AI Deduction Suggestions Endpoint
@tax_bp.route("/api/tax/deductions", methods=["POST"])
@rate_limit(requests_per_minute=TAX_CONFIG["RATE_LIMITS"]["deduction_analysis"])
@cache_response(timeout=TAX_CONFIG["CACHE_SETTINGS"]["deduction_analysis"])
def ai_deduction_suggestions():
    """Calculate deductions based on expense data"""
    try:
        schema = DeductionAnalysisSchema()
        data = schema.load(request.json)
        deduction_analysis = tax_service.analyze_deductions(data)
        return jsonify({"suggestions": deduction_analysis}), 200
    except Exception as e:
        return handle_api_error(e)


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

        tax_result: TaxCalculationResult = tax_service.calculate_quarterly_tax(
            income, expenses
        )

        return (
            jsonify(
                {
                    "quarter": quarter,
                    "year": year,
                    "income": float(income),
                    "expenses": float(expenses),
                    "quarterly_tax": tax_result["quarterly_amount"],
                    "annual_tax": tax_result["annual_tax"],
                    "effective_rate": tax_result["effective_rate"],
                }
            ),
            200,
        )
    except Exception as e:
        logging.error(f"Error calculating quarterly tax estimate: {str(e)}")
        return jsonify({"error": "Failed to calculate quarterly tax estimate."}), 500


def calculate_tax_bracket(income: float) -> tuple:
    """Calculate tax bracket and effective rate based on income"""
    for min_income, max_income, rate in TAX_CONFIG["TAX_BRACKETS"]:
        if min_income <= income <= max_income:
            return rate, f"${min_income:,} - ${max_income:,}"
    return (
        TAX_CONFIG["TAX_BRACKETS"][-1][2],
        f"Over ${TAX_CONFIG['TAX_BRACKETS'][-1][0]:,}",
    )


@tax_bp.route("/calculate-effective-rate", methods=["POST"])
def calculate_effective_rate():
    """Calculate effective tax rate based on income and deductions"""
    try:
        data = request.json
        gross_income = Decimal(data.get("gross_income", 0))
        deductions = Decimal(data.get("deductions", 0))

        taxable_income = max(Decimal("0"), gross_income - deductions)
        tax_rate, bracket = calculate_tax_bracket(taxable_income)

        return jsonify(
            {
                "taxable_income": float(taxable_income),
                "tax_bracket": bracket,
                "tax_rate": float(tax_rate),
                "estimated_tax": float(taxable_income * tax_rate),
            }
        )
    except Exception as e:
        logging.error(f"Error calculating effective tax rate: {str(e)}")
        return jsonify({"error": "Failed to calculate effective tax rate"}), 500


@tax_bp.route("/api/tax/document", methods=["POST"])
@rate_limit(requests_per_minute=TAX_CONFIG["RATE_LIMITS"]["document_generation"])
def generate_tax_document():
    """Generate tax documents based on user input"""
    try:
        schema = TaxDocumentSchema()
        data = schema.load(request.json)
        document = tax_service.generate_tax_document(data)
        return jsonify(document), 200
    except Exception as e:
        return handle_api_error(e)


@tax_bp.route("/export-tax-report", methods=["POST"])
def export_tax_report():
    try:
        data = request.json
        format_type = data.get("format", "pdf")
        tax_data = tax_service.generate_tax_report(data)

        # Log export attempt
        audit_logger.log_tax_analysis(
            data["user_id"],
            f"tax_report_export_{format_type}",
            {"year": data.get("year")},
        )

        if format_type == "pdf":
            return export_service.export_pdf(tax_data)
        elif format_type == "excel":
            return export_service.export_excel(tax_data)
        else:
            return export_service.export_json(tax_data)
    except Exception as e:
        logging.error(f"Error exporting tax report: {str(e)}")
        return jsonify({"error": "Failed to export tax report."}), 500


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(tax_bp)
    app.run(debug=True)
