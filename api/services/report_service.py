from typing import Dict, Any
import logging
from datetime import datetime
from api.utils.db_utils import get_db_connection
from api.utils.cache_utils import CacheManager
from shared.services.reportsService import ReportsService


class ReportService(ReportsService):
    def __init__(self):
        super().__init__()
        self.db = get_db_connection()
        self.cache = CacheManager()

    def validate_report_config(self, report_type: str, data: Dict[str, Any]) -> bool:
        """Validate report configuration using shared rules"""
        return super().validate_report_config(report_type, data)

    def generate_tax_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tax summary report"""
        try:
            user_id = data.get("user_id")
            year = data.get("year", datetime.now().year)

            # Get income data
            income_data = self._get_income_summary(user_id, year)

            # Get expense data
            expense_data = self._get_expense_summary(user_id, year)

            # Get deduction data
            deduction_data = self._get_deduction_summary(user_id, year)

            report = {
                "income_summary": income_data,
                "expense_summary": expense_data,
                "deduction_summary": deduction_data,
                "generated_at": datetime.now().isoformat(),
                "tax_year": year,
            }

            # Cache the report
            self.cache.set_report_cache(user_id, "tax_summary", report)
            return report
        except Exception as e:
            logging.error(f"Error generating tax summary: {e}")
            return {}
