from typing import Dict, Any
import logging
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
        return super().validateReportConfig(report_type, data)

    def generate_tax_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tax summary report"""
        try:
            cached_data = self.cache.get_report_cache(
                data['user_id'], 
                'tax_summary', 
                data,
                self.config['tax_summary']['cacheDuration']
            )
            if cached_data:
                return cached_data
        except Exception as e:
            logging.error(f"Error generating tax summary: {e}")
            return {}
