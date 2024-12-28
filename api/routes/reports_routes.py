from flask import Blueprint, request, jsonify
from api.config.report_config import REPORT_CONFIG
from api.services.report_service import ReportService
from api.services.analytics_service import AnalyticsService
from api.services.export_service import ExportService
from api.utils.error_handler import handle_api_error
from api.utils.rate_limit import rate_limit
from api.utils.cache_utils import cache_response

# Initialize services
report_service = ReportService()
analytics_service = AnalyticsService()
export_service = ExportService()

@rate_limit(requests_per_minute=REPORT_CONFIG['RATE_LIMITS']['generate_report'])
@cache_response(timeout=REPORT_CONFIG['CACHE_SETTINGS']['tax_summary'])
def generate_tax_summary():
    """Generate tax summary report"""
    try:
        summary = report_service.generate_tax_summary(request.json)
        return jsonify(summary)
    except Exception as e:
        return handle_api_error(e)
