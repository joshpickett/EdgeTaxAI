import os
import sys
from api.setup_path import setup_python_path
setup_python_path(__file__)

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import logging
from typing import Dict, Any, List, Union
from api.schemas.report_schemas import (
    TaxSummarySchema, ScheduleCSchema, 
    CustomReportSchema, AnalyticsRequestSchema
)
from api.services.report_service import ReportService
from api.services.analytics_service import AnalyticsService
from api.services.export_service import ExportService
from api.utils.error_handler import (
    handle_api_error,
    handle_report_error,
    ReportGenerationError
)

# Initialize services
report_service = ReportService()
analytics_service = AnalyticsService()
export_service = ExportService()

reports_bp = Blueprint('reports', __name__)

@reports_bp.route("/reports/<report_type>", methods=["POST"])
def generate_report_endpoint():
    try:
        data = request.json
        report = report_service.generate_report(
            data.get('type'),
            data.get('params', {})
        )
        return jsonify(report)
    except Exception as e:
        return handle_report_error(e)

@reports_bp.route("/tax-summary", methods=["POST"])
def generate_tax_summary():
    """Generate tax summary report"""
    try:
        schema = TaxSummarySchema()
        data = schema.load(request.json)
        
        summary = report_service.generate_tax_summary(
            data['user_id'], 
            data['year']
        )
        return jsonify(summary)
    except Exception as e:
        logging.error(f"Error generating tax summary: {e}")
        return handle_report_error(e)

@reports_bp.route("/irs/schedule-c", methods=["POST"])
def generate_schedule_c():
    """Generate IRS Schedule C report"""
    try:
        schema = ScheduleCSchema()
        data = schema.load(request.json)
        
        schedule_c = report_service.generate_schedule_c(data['user_id'], data['year'])
        return jsonify(schedule_c)
    except Exception as e:
        logging.error(f"Error generating Schedule C: {e}")
        return handle_report_error(e)

@reports_bp.route("/custom-report", methods=["POST"])
def generate_custom_report():
    """Generate custom report based on user specifications"""
    try:
        schema = CustomReportSchema()
        data = schema.load(request.json)
        
        report = report_service.generate_custom_report(
            data['user_id'], 
            data['start_date'], 
            data['end_date'],
            data.get('categories', []),
            data.get('report_type', 'detailed')
        )
        
        if data.get('format', 'json') == 'csv':
            csv_data = report_service.export_to_csv(report)
            return send_file(
                io.StringIO(csv_data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'custom_report_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        
        return jsonify(report)
    except Exception as e:
        logging.error(f"Error generating custom report: {e}")
        return handle_report_error(e)

@reports_bp.route("/analytics", methods=["POST"])
def generate_analytics():
    """Generate expense pattern analytics"""
    try:
        schema = AnalyticsRequestSchema()
        data = schema.load(request.json)
        
        analytics = report_service.generate_analytics(data['user_id'], data['year'])
        return jsonify(analytics)
    except Exception as e:
        logging.error(f"Error generating analytics: {e}")
        return handle_report_error(e)

@reports_bp.route("/tax-savings", methods=["POST"])
def analyze_tax_savings():
    """Analyze potential tax saving opportunities"""
    try:
        data = request.json
        user_id = data.get('user_id')
        year = data.get('year', datetime.now().year)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
            
        savings = report_service.analyze_tax_savings(user_id, year)
        return jsonify(savings)
    except Exception as e:
        logging.error(f"Error analyzing tax savings: {e}")
        return handle_report_error(e)

@reports_bp.route("/export", methods=["POST"])
def export_report():
    """Export report in specified format (PDF, Excel, JSON)"""
    try:
        data = request.json
        user_id = data.get('user_id')
        report_type = data.get('report_type')
        format_type = data.get('format', 'pdf')
        
        if not user_id or not report_type:
            return jsonify({"error": "User ID and report type are required"}), 400
            
        # Generate report data
        report_data = report_service.generate_report(user_id, report_type)
        
        # Export based on format
        if format_type == 'pdf':
            return export_service.export_pdf(report_data)
        elif format_type == 'excel':
            return export_service.export_excel(report_data)
        elif format_type == 'json':
            return export_service.export_json(report_data)
        else:
            return jsonify({"error": "Unsupported format"}), 400
            
    except Exception as e:
        logging.error(f"Error exporting report: {e}")
        return handle_report_error(e)

@reports_bp.route("/advanced-analytics", methods=["POST"])
def generate_advanced_analytics():
    """Generate advanced analytics with trend analysis and predictions"""
    try:
        schema = AnalyticsRequestSchema()
        data = schema.load(request.json)
        
        analytics = analytics_service.generate_advanced_analytics(
            data['user_id'],
            data['year'],
            include_predictions=data.get('include_predictions')
        )
        
        return jsonify(analytics)
    except Exception as e:
        logging.error(f"Error generating advanced analytics: {e}")
        return handle_report_error(e)

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(reports_bp)
    app.run(debug=True)
