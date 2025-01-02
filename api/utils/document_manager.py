from typing import Dict, Any, List
import logging
import os
import uuid
from datetime import datetime
from api.services.category.category_manager import CategoryManager
from api.services.validation.validation_manager import ValidationManager
from api.services.error_handling_service import ErrorHandlingService
from api.services.performance_logger import PerformanceLogger
from api.services.error_metrics_collector import ErrorMetricsCollector
from api.services.document.document_optimization_service import (
    DocumentOptimizationService,
)


class DocumentManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_logger = PerformanceLogger()
        self.error_metrics = ErrorMetricsCollector()
        self.category_manager = CategoryManager()
        self.validation_manager = ValidationManager()
        self.optimization_service = DocumentOptimizationService()
        self.storage_path = os.getenv("DOCUMENT_STORAGE_PATH", "storage/documents")

    async def store_document(
        self, content: bytes, filename: str, mime_type: str
    ) -> str:
        """Store document with enhanced metadata"""
        try:
            start_time = datetime.utcnow()
            document_id = self._generate_document_id()

            # Optimize document before storage
            optimized_content = await self.optimization_service.optimize_document(
                content, mime_type
            )

            # Store optimized document
            await self._store_optimized_document(optimized_content, document_id)

            await self.performance_logger.log_metrics(
                {
                    "operation": "store_document",
                    "duration": (datetime.utcnow() - start_time).total_seconds(),
                }
            )
            return document_id

        except Exception as e:
            await self.error_metrics.collect_error(e, "STORAGE")
            self.logger.error(f"Error storing document: {str(e)}")
            raise

    async def validate_document(self, document_id: str) -> Dict[str, Any]:
        """Validate document with enhanced category support"""
        try:
            start_time = datetime.utcnow()
            validation_result = await self._perform_validation(document_id)

            # Log performance metrics
            await self.performance_logger.log_metrics(
                {
                    "operation": "validate_document",
                    "duration": (datetime.utcnow() - start_time).total_seconds(),
                    "document_id": document_id,
                }
            )

            return validation_result

        except Exception as e:
            await self.error_metrics.collect_error(e, "VALIDATION")
            raise

    def _generate_storage_path(self, document_id: str, category: str = None) -> str:
        """Generate storage path based on category"""
        base_path = self.storage_path
        if category:
            return os.path.join(base_path, category, document_id)
        return os.path.join(base_path, document_id)

    def _generate_document_id(self, category: str = None) -> str:
        """Generate document ID with category prefix"""
        unique_id = str(uuid.uuid4())
        if category:
            return f"{category.lower()}_{unique_id}"
        return unique_id

    async def get_category_documents(self, category: str) -> List[Dict[str, Any]]:
        """Get all documents in a category"""
        try:
            category_path = os.path.join(self.storage_path, category)
            if not os.path.exists(category_path):
                return []

            documents = []
            for filename in os.listdir(category_path):
                document_id = filename.split(".")[0]
                document = await self._get_document(document_id)
                if document:
                    documents.append(document)

            return documents

        except Exception as e:
            self.logger.error(f"Error getting category documents: {str(e)}")
            raise
