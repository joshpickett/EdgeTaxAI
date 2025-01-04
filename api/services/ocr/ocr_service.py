from google.cloud import vision
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...utils.ocr_processor import OCRProcessor
from ...utils.ai_document_classifier import DocumentClassifier
from ...models.documents import Document
from ...schemas.ocr_schemas import OCRResultSchema
from ...exceptions.ocr_exceptions import OCRProcessingError, DocumentValidationError
from ...utils.monitoring import MonitoringSystem
from ...utils.error_metrics_collector import ErrorMetricsCollector
import logging

class OCRService:
    def __init__(self):
        self.ocr_processor = OCRProcessor()
        self.document_classifier = DocumentClassifier()
        self.monitoring = MonitoringSystem()
        self.error_collector = ErrorMetricsCollector()
        self.client = vision.ImageAnnotatorClient()
        self.logger = logging.getLogger(__name__)

    async def process_single_receipt(self, file_content: bytes, user_id: str) -> Dict[str, Any]:
        """Process a single receipt and extract data"""
        try:
            start_time = datetime.now()
            self.monitoring.log_performance_metric("ocr_processing_start", start_time)

            # Extract text using OCR
            extracted_data = self.ocr_processor.process_receipt(file_content)
            
            if not extracted_data:
                raise DocumentValidationError("Failed to extract data from receipt")
            
            # Classify document
            doc_type, confidence = self.document_classifier.classify_document(
                extracted_data.get('raw_text', '')
            )

            # Process extracted data
            processed_result = {
                'document_type': doc_type,
                'confidence_score': confidence,
                'extracted_data': extracted_data,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }

            self.monitoring.log_performance_metric("ocr_processing_end", start_time, datetime.now())
            return processed_result
        except Exception as e:
            await self.error_collector.collect_error(e, "ocr_processing")
            self.monitoring.alert("error", "OCR processing failed", {"error": str(e)})
            self.logger.error(f"Receipt processing error: {e}")
            raise OCRProcessingError(f"Failed to process receipt: {str(e)}")

    async def process_batch(self, files: List[Dict], user_id: str) -> List[Dict[str, Any]]:
        """Process multiple receipts in batch"""
        try:
            batch_results = []
            for file in files:
                result = await self.process_single_receipt(file['content'], user_id)
                batch_results.append(result)
            
            return batch_results
        except Exception as e:
            self.logger.error(f"Batch processing error: {e}")
            raise
