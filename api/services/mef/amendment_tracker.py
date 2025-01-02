from typing import Dict, Any, List
import logging
from datetime import datetime
from api.models.mef_submissions import MeFSubmission, SubmissionStatus
from api.utils.document_manager import DocumentManager
from api.services.mef.xml_optimizer import XMLOptimizer
from api.services.mef.schema_manager import SchemaManager
from xml.etree import ElementTree


class AmendmentTracker:
    """Track and manage tax form amendments"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.document_manager = DocumentManager()
        self.xml_optimizer = XMLOptimizer()
        self.schema_manager = SchemaManager()

    async def create_amendment(
        self, original_submission_id: str, amendment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new amendment"""
        try:
            # Get original submission
            original = await self._get_submission(original_submission_id)
            if not original:
                raise ValueError("Original submission not found")

            # Generate amendment XML
            amendment_xml = self._generate_amendment_xml(
                original.xml_content, amendment_data
            )

            # Validate amendment
            validation_result = self.schema_manager.validate_schema(
                amendment_xml, original.form_type
            )
            if not validation_result["is_valid"]:
                return {"success": False, "errors": validation_result["errors"]}

            # Create amendment submission
            amendment = MeFSubmission(
                user_id=original.user_id,
                form_type=original.form_type,
                status=SubmissionStatus.PENDING,
                xml_content=amendment_xml,
                is_amendment=True,
                original_submission_id=original_submission_id,
            )

            # Store amendment
            await self._store_amendment(amendment)

            return {
                "success": True,
                "amendment_id": amendment.id,
                "status": amendment.status.value,
            }

        except Exception as e:
            self.logger.error(f"Error creating amendment: {str(e)}")
            raise

    def generate_diff(self, original_xml: str, amended_xml: str) -> Dict[str, Any]:
        """Generate difference between original and amended versions"""
        try:
            diff_result = self._calculate_xml_diff(original_xml, amended_xml)

            return {
                "changes": diff_result["changes"],
                "summary": diff_result["summary"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            self.logger.error(f"Error generating diff: {str(e)}")
            raise

    def _generate_amendment_xml(
        self, original_xml: str, amendment_data: Dict[str, Any]
    ) -> str:
        """Generate amendment XML"""
        try:
            # Parse original XML
            root = ElementTree.fromstring(original_xml)

            # Apply amendments
            self._apply_amendments(root, amendment_data)

            # Add amendment indicator
            amendment_indicator = ElementTree.SubElement(root, "AmendmentIndicator")
            amendment_indicator.text = "true"

            # Add original submission reference
            original_ref = ElementTree.SubElement(root, "OriginalSubmissionId")
            original_ref.text = str(amendment_data.get("original_submission_id"))

            return ElementTree.tostring(root, encoding="unicode")

        except Exception as e:
            self.logger.error(f"Error generating amendment XML: {str(e)}")
            raise

    def _calculate_xml_diff(
        self, original_xml: str, amended_xml: str
    ) -> Dict[str, Any]:
        """Calculate differences between XML versions"""
        try:
            original_root = ElementTree.fromstring(original_xml)
            amended_root = ElementTree.fromstring(amended_xml)

            changes = []

            def compare_elements(orig, amend, path=""):
                if orig.tag != amend.tag:
                    changes.append(
                        {
                            "type": "tag_change",
                            "path": path,
                            "original": orig.tag,
                            "amended": amend.tag,
                        }
                    )

                if orig.text != amend.text:
                    changes.append(
                        {
                            "type": "value_change",
                            "path": path,
                            "original": orig.text,
                            "amended": amend.text,
                        }
                    )

                # Compare children recursively
                orig_children = list(orig)
                amend_children = list(amend)

                for child_orig, child_amend in zip(orig_children, amend_children):
                    compare_elements(
                        child_orig, child_amend, f"{path}/{child_orig.tag}"
                    )

            compare_elements(original_root, amended_root)

            return {"changes": changes, "summary": self._generate_diff_summary(changes)}

        except Exception as e:
            self.logger.error(f"Error calculating XML diff: {str(e)}")
            raise

    def _generate_diff_summary(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of changes"""
        return {
            "total_changes": len(changes),
            "value_changes": len([c for c in changes if c["type"] == "value_change"]),
            "structure_changes": len([c for c in changes if c["type"] == "tag_change"]),
            "modified_paths": list(set(c["path"] for c in changes)),
        }

    async def _store_amendment(self, amendment: MeFSubmission) -> None:
        """Store amendment in document manager"""
        try:
            # Store XML content
            document_id = await self.document_manager.store_document(
                amendment.xml_content,
                f"amendment_{amendment.id}.xml",
                "application/xml",
            )

            # Update amendment with document reference
            amendment.document_id = document_id

            # Store in database
            await self._save_submission(amendment)

        except Exception as e:
            self.logger.error(f"Error storing amendment: {str(e)}")
            raise
