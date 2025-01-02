from typing import Dict, Any, List
import logging
from datetime import datetime
from api.models.documents import Document, DocumentStatus
from api.services.form.form_document_service import FormDocumentService


class DocumentValidationWorkflow:
    """Service for managing document validation workflows"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.document_service = FormDocumentService()

    async def process_document(
        self, document_id: int, form_type: str
    ) -> Dict[str, Any]:
        """Process document through validation workflow"""
        try:
            # Initial validation
            validation_result = await self.document_service.validate_document(
                document_id, form_type
            )

            # Update document status
            await self._update_document_status(
                document_id, self._determine_status(validation_result)
            )

            # Generate workflow steps
            workflow_steps = self._generate_workflow_steps(validation_result)

            return {
                "validation_result": validation_result,
                "workflow_steps": workflow_steps,
                "next_action": self._determine_next_action(workflow_steps),
            }

        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            raise

    def _determine_status(self, validation_result: Dict[str, Any]) -> DocumentStatus:
        """Determine document status based on validation"""
        if validation_result["is_valid"]:
            return DocumentStatus.VALIDATED
        elif validation_result.get("errors", []):
            return DocumentStatus.INVALID
        else:
            return DocumentStatus.NEEDS_REVIEW

    def _generate_workflow_steps(
        self, validation_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate workflow steps based on validation results"""
        steps = []

        # Add validation steps
        if validation_result.get("errors", []):
            for error in validation_result["errors"]:
                steps.append(
                    {
                        "type": "correction",
                        "status": "pending",
                        "description": error["message"],
                        "priority": "high",
                    }
                )

        # Add review steps
        if validation_result.get("warnings", []):
            for warning in validation_result["warnings"]:
                steps.append(
                    {
                        "type": "review",
                        "status": "pending",
                        "description": warning["message"],
                        "priority": "medium",
                    }
                )

        return steps

    def _determine_next_action(
        self, workflow_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine next action in workflow"""
        pending_steps = [step for step in workflow_steps if step["status"] == "pending"]

        if not pending_steps:
            return {"type": "complete", "message": "Document validation complete"}

        next_step = min(
            pending_steps, key=lambda x: 0 if x["priority"] == "high" else 1
        )

        return {
            "type": next_step["type"],
            "description": next_step["description"],
            "priority": next_step["priority"],
        }

    async def _update_document_status(
        self, document_id: int, status: DocumentStatus
    ) -> None:
        """Update document status"""
        # Implementation would update document status in database
        pass
