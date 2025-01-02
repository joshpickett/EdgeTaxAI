from typing import Dict, Any, List
import logging
from datetime import datetime
from api.models.tax_forms import TaxForms, FormType
from api.services.mef.validation_rules import ValidationRules
from api.services.document_requirements_mapper import DocumentRequirementsMapper


class DocumentChecklistService:
    """Service for managing tax document requirements and checklists"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ValidationRules()
        self.requirements_mapper = DocumentRequirementsMapper()
        self.international_requirements = self._load_international_requirements()
        self.farm_requirements = self._load_farm_requirements()

    async def generate_checklist(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Generate document checklist based on user's tax situation"""
        try:
            # Get user's answers and form types
            answers = await self._get_user_answers(user_id, tax_year)
            form_types = await self._get_user_form_types(user_id, tax_year)

            # Get required documents for each form type
            all_requirements = {
                "required": [],
                "optional": [],
                "international": [],
                "farm": []
            }

            for form_type in form_types:
                requirements = self.requirements_mapper.get_required_documents(
                    form_type, answers
                )
                
                # Add international requirements if needed
                if self._needs_international_documents(answers):
                    requirements["international"] = self._get_international_requirements(answers)
                
                # Add farm requirements if needed
                if self._needs_farm_documents(answers):
                    requirements["farm"] = self._get_farm_requirements(answers)

                all_requirements["required"].extend(requirements.get("required", []))
                all_requirements["optional"].extend(requirements.get("optional", []))
                all_requirements["international"].extend(requirements.get("international", []))
                all_requirements["farm"].extend(requirements.get("farm", []))

            required_documents = all_requirements["required"]
            optional_documents = all_requirements["optional"]
            international_documents = all_requirements["international"]
            farm_documents = all_requirements["farm"]

            return {
                "required": self._prioritize_documents(required_documents),
                "optional": self._prioritize_documents(optional_documents),
                "international": self._prioritize_documents(international_documents),
                "farm": self._prioritize_documents(farm_documents),
                "status": self._get_document_status(user_id, required_documents),
            }

        except Exception as e:
            self.logger.error(f"Error generating document checklist: {str(e)}")
            raise

    def _needs_international_documents(self, answers: Dict[str, Any]) -> bool:
        """Determine if international documents are needed"""
        return (
            answers.get("has_foreign_income", False) or
            answers.get("has_foreign_accounts", False) or
            answers.get("has_foreign_assets", False)
        )

    def _needs_farm_documents(self, answers: Dict[str, Any]) -> bool:
        """Determine if farm documents are needed"""
        return (
            answers.get("has_farm_income", False) or
            answers.get("has_agricultural_payments", False) or
            answers.get("has_farm_expenses", False)
        )

    def _get_international_requirements(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Get international document requirements"""
        requirements = {
            "required": [],
            "optional": []
        }

        if answers.get("has_foreign_income"):
            requirements["required"].extend(self.international_requirements["foreign_income"])

        if answers.get("has_foreign_accounts"):
            requirements["required"].extend(self.international_requirements["foreign_accounts"])

        return requirements

    def _get_farm_requirements(self, answers: Dict[str, Any]) -> Dict[str, Any]:
        """Get farm document requirements"""
        requirements = {
            "required": [],
            "optional": []
        }

        if answers.get("has_farm_income"):
            requirements["required"].extend(self.farm_requirements["farm_income"])

        return requirements

    def _prioritize_documents(
        self, documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort documents by priority"""
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        return sorted(
            documents, key=lambda x: priority_scores.get(x["priority"], 0), reverse=True
        )

    async def _get_document_status(
        self, user_id: int, required_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhanced document status check with international document support"""
        submitted_documents = await self._get_submitted_documents(user_id)

        status = {
            "total": len(required_documents),
            "submitted": 0,
            "missing": [],
            "incomplete": [],
            "international": {"required": [], "submitted": [], "missing": []},
        }

        for doc in required_documents:
            if self._is_international_document(doc["type"]):
                status["international"]["required"].append(doc["type"])
                if doc["type"] in submitted_documents:
                    status["international"]["submitted"].append(doc["type"])
                else:
                    status["international"]["missing"].append(doc["type"])
            else:
                if doc["type"] in submitted_documents:
                    status["submitted"] += 1
                else:
                    status["missing"].append(doc["type"])

        return status

    async def _get_user_tax_forms(self, user_id: int, tax_year: int) -> List[TaxForms]:
        """Get user's tax forms"""
        # Implementation would fetch actual tax forms
        # This is a placeholder
        return []

    async def _get_submitted_documents(self, user_id: int) -> List[str]:
        """Get list of submitted documents"""
        # Implementation would fetch actual submitted documents
        # This is a placeholder
        return []

    def _is_international_document(self, document_type: str) -> bool:
        """Check if the document type is international"""
        international_documents = [
            "foreign_bank_statements",
            "foreign_tax_returns",
            "foreign_income_docs",
            "foreign_tax_receipts",
            "foreign_income_statements",
            "foreign_currency_docs",
            "treaty_documentation",
        ]
        return document_type in international_documents

    def _load_international_requirements(self) -> Dict[str, Any]:
        """Load international document requirements"""
        return {
            "foreign_income": [
                {
                    "type": "FOREIGN_INCOME_STATEMENT",
                    "priority": "high",
                    "metadata": {
                        "retention_years": 7,
                        "requires_translation": True
                    }
                }
            ],
            "foreign_accounts": [
                {
                    "type": "FBAR",
                    "priority": "high",
                    "metadata": {
                        "retention_years": 6,
                        "threshold": 10000
                    }
                }
            ]
        }

    def _load_farm_requirements(self) -> Dict[str, Any]:
        """Load farm document requirements"""
        return {
            "farm_income": [
                {
                    "type": "SCHEDULE_F",
                    "priority": "high",
                    "metadata": {
                        "retention_years": 7,
                        "requires_inventory": True
                    }
                }
            ]
        }
