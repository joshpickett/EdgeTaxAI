from typing import Dict, Any, List
from ..services.ocr.ocr_service import OCRService
from ..utils.error_handler import handle_api_error
from ..schemas.ocr_schemas import OCRResultSchema
import logging

class OCRController:
    def __init__(self):
        self.ocr_service = OCRService()

    async def handle_receipt_processing(self, file_content: bytes, user_id: str) -> Dict[str, Any]:
        """Handle single receipt processing request"""
        try:
            result = await self.ocr_service.process_single_receipt(file_content, user_id)
            return OCRResultSchema().dump(result)
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
