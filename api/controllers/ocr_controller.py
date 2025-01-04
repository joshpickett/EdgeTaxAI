from typing import Dict, Any, List
from ..services.ocr.ocr_service import OCRService
from ..utils.error_handler import handle_api_error
from ..utils.monitoring import MonitoringSystem
from ..utils.cache_utils import CacheManager
from ..schemas.ocr_schemas import OCRResultSchema
from ..exceptions.ocr_exceptions import OCRBaseException
import logging

logger = logging.getLogger(__name__)

class OCRController:
    def __init__(self):
        self.ocr_service = OCRService()
        self.monitoring = MonitoringSystem()
        self.cache = CacheManager()

    async def handle_receipt_processing(self, file_content: bytes, user_id: str) -> Dict[str, Any]:
        """Handle single receipt processing request"""
        try:
            # Check cache first
            cache_key = f"receipt_{hash(file_content)}_{user_id}"
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

            result = await self.ocr_service.process_single_receipt(file_content, user_id)
            processed_result = OCRResultSchema().dump(result)
            self.cache.set(cache_key, processed_result, timeout=3600)
            return processed_result
        except Exception as e:
            logging.error(f"Receipt processing error: {e}")
            raise

    async def handle_batch_processing(self, files: List[Dict], user_id: str) -> Dict[str, Any]:
        """Handle batch receipt processing request"""
        try:
            results = await self.ocr_service.process_batch(files, user_id)
            return {"batch_results": OCRResultSchema(many=True).dump(results)}
        except Exception as e:
            logging.error(f"Batch processing error: {e}")
            raise

    def validate_receipt(self, file_content: bytes, filename: str) -> bool:
        """Validate receipt before processing"""
        try:
            # Add validation logic here
            return True
        except Exception as e:
            logging.error(f"Receipt validation error: {e}")
            return False
