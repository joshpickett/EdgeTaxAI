from typing import Dict, Any, List
import logging
from datetime import datetime
import yaml
import os
from decimal import Decimal
from api.services.document_requirement_conditions import DocumentRequirementConditions
from api.services.category.category_manager import CategoryManager
from api.services.validation.validation_manager import ValidationManager


class DocumentRequirementsMapper:
    """Maps document requirements based on MEF templates and form types"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_path = os.path.join("api", "config", "document_requirements")
        self.tax_year = str(datetime.now().year)
        self.condition_service = DocumentRequirementConditions()
        self.category_manager = CategoryManager()
        self.validation_manager = ValidationManager()
        self.metadata_config = self._load_config("metadata.yml")

        # Load configurations
        self.base_requirements = self._load_config("base_requirements.yml")
        self.schedule_requirements = self._load_config("schedule_requirements.yml")
        self.international_requirements = self._load_config("international_requirements.yml")
        self.document_categories = self._initialize_categories()

    def get_required_documents(
        self, form_type: str, answers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get required documents based on form type and questionnaire answers"""
        try:
            required_documents = []
            optional_documents = []

            # Get category-specific requirements
            category_requirements = self.category_manager.get_category_rules(form_type)
            if category_requirements:
                # Enhanced category validation
                for document in category_requirements.get("required", []):
                    metadata = self.metadata_config.get(document.get("type", {}))
                    if metadata:
                        document["metadata"] = {
                            **document.get("metadata", {}),
                            **metadata,
                        }

                required_documents.extend(category_requirements.get("required", []))
                optional_documents.extend(category_requirements.get("optional", []))

            # Process base requirements
            if form_type in self.base_requirements:
                base = self.base_requirements[form_type]
                for document in base.get("required", []):
                    if "conditions" in document:
                        category = document.get("category", "uncategorized")
                        # Validate against category rules
                        await self.validation_manager.validate_document(
                            document, category
                        )

                        conditional_documents = (
                            self.condition_service.evaluate_conditions(
                                document["conditions"], answers
                            )
                        )
                        required_documents.extend(conditional_documents)
                    else:
                        required_documents.append(document)
                
            # Add farm requirements if applicable
            if self._needs_farm_documents(answers):
                farm_documents = self._get_farm_requirements(answers)
                required_documents.extend(farm_documents["required"])
                optional_documents.extend(farm_documents.get("optional", []))

            # Add schedule requirements based on answers
            schedule_documents = self._get_schedule_requirements(answers)
            required_documents.extend(schedule_documents["required"])
            optional_documents = schedule_documents["optional"]

            # Add international requirements if applicable
            if self._needs_international_documents(answers):
                international_documents = self._get_international_requirements(answers)
                required_documents.extend(international_documents["required"])
                optional_documents.extend(international_documents.get("optional", []))

            # Add conditional requirements based on answers
            if answers.get("has_self_employment"):
                self._add_self_employment_requirements(
                    required_documents, optional_documents
                )

            if answers.get("has_rental_income"):
                self._add_rental_requirements(required_documents, optional_documents)

            if answers.get("has_business_expenses"):
                self._add_business_expense_requirements(
                    required_documents, optional_documents
                )

            return {
                "required": required_documents,
                "optional": optional_documents,
                "total_required": len(required_documents),
                "total_optional": len(optional_documents),
            }

        except Exception as exception:
            self.logger.error(f"Error getting required documents: {str(exception)}")
            raise

    async def validate_category_requirements(
        self, documents: List[Dict[str, Any]], category: str
    ) -> Dict[str, Any]:
        """Validate documents against category requirements"""
        try:
            validation_result = {"is_valid": True, "errors": [], "warnings": []}

            category_rules = self.category_manager.get_category_rules(category)
            for document in documents:
                document_validation = await self.validation_manager.validate_document(
                    document, category
                )

                if not document_validation["is_valid"]:
                    validation_result["is_valid"] = False
                    validation_result["errors"].extend(document_validation["errors"])
                validation_result["warnings"].extend(document_validation["warnings"])

            return validation_result

        except Exception as exception:
            self.logger.error(
                f"Error validating category requirements: {str(exception)}"
            )
            raise

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            config_file = os.path.join(self.config_path, self.tax_year, filename)
            with open(config_file, "r") as file:
                return yaml.safe_load(file)
        except Exception as exception:
            self.logger.error(f"Error loading config {filename}: {str(exception)}")
            # Fall back to previous year if current year config doesn't exist
            previous_year = str(int(self.tax_year) - 1)
            config_file = os.path.join(self.config_path, previous_year, filename)
            with open(config_file, "r") as file:
                return yaml.safe_load(file)

    def _get_schedule_requirements(
        self, answers: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get schedule-specific document requirements"""
        required = []
        optional = []

        # Check Schedule C requirements
        if answers.get("has_business_income"):
            schedule_c = self.schedule_requirements["SCHEDULE_C"]
            required.extend(schedule_c["required"])
            optional.extend(schedule_c.get("optional", []))

        # Check Schedule E requirements
        if answers.get("has_rental_income"):
            schedule_e = self.schedule_requirements["SCHEDULE_E"]
            required.extend(schedule_e["required"])
            optional.extend(schedule_e.get("optional", []))

        return {"required": required, "optional": optional}

    def _needs_international_documents(self, answers: Dict[str, Any]) -> bool:
        """Determine if international documents are needed"""
        try:
            # Enhanced international document detection
            triggers = {
                "has_foreign_accounts": False,
                "has_foreign_income": False,
                "has_foreign_assets": False,
                "foreign_account_value": Decimal("0"),
            }

            for key in triggers:
                if key == "foreign_account_value":
                    value = Decimal(str(answers.get(key, 0)))
                    if value > 10000:
                        return True
                elif answers.get(key):
                    return True

            return False
        except Exception as exception:
            self.logger.error(
                f"Error checking international documents: {str(exception)}"
            )
            return False

    def _get_international_requirements(
        self, answers: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get international document requirements"""
        required = []
        optional = []

        # Add Form 8938 requirements if applicable
        if answers.get("has_foreign_assets"):
            form_8938 = self.international_requirements["FORM_8938"]
            required.extend(form_8938["required"])
            optional.extend(form_8938.get("optional", []))

        # Add FBAR requirements if applicable
        if answers.get("has_foreign_accounts"):
            foreign_bank_account_report = self.international_requirements["FBAR"]
            required.extend(foreign_bank_account_report["required"])
            optional.extend(foreign_bank_account_report.get("optional", []))

        return {"required": required, "optional": optional}

    def validate_documents(
        self,
        required_documents: List[Dict[str, Any]],
        submitted_documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Validate submitted documents against requirements"""
        try:
            submitted_types = {document["type"] for document in submitted_documents}
            required_types = {document["type"] for document in required_documents}

            missing_documents = [
                document
                for document in required_documents
                if document["type"] not in submitted_types
            ]

            return {
                "is_complete": len(missing_documents) == 0,
                "missing_documents": missing_documents,
                "submitted_count": len(submitted_documents),
                "required_count": len(required_documents),
            }

        except Exception as exception:
            self.logger.error(f"Error validating documents: {str(exception)}")
            raise

    def _add_self_employment_requirements(
        self, required: List[Dict], optional: List[Dict]
    ) -> None:
        """Add self-employment specific requirements"""
        self_employment_documents = self.schedule_requirements["SCHEDULE_C"]
        required.extend(
            [
                document
                for document in self_employment_documents["required"]
                if document not in required
            ]
        )
        optional.extend(
            [
                document
                for document in self_employment_documents.get("optional", [])
                if document not in optional
            ]
        )

    def _add_rental_requirements(
        self, required: List[Dict], optional: List[Dict]
    ) -> None:
        """Add rental income specific requirements"""
        rental_documents = self.schedule_requirements["SCHEDULE_E"]
        required.extend(
            [
                document
                for document in rental_documents["required"]
                if document not in required
            ]
        )
        optional.extend(
            [
                document
                for document in rental_documents.get("optional", [])
                if document not in optional
            ]
        )

    def _add_business_expense_requirements(
        self, required: List[Dict], optional: List[Dict]
    ) -> None:
        """Add business expense specific requirements"""
        expense_documents = {
            "required": [
                {"type": "expense_receipts", "priority": "high"},
                {"type": "bank_statements", "priority": "high"},
                {"type": "expense_log", "priority": "medium"},
            ],
            "optional": [
                {"type": "mileage_log", "priority": "low"},
                {"type": "home_office", "priority": "low"},
            ],
        }
        required.extend(expense_documents["required"])
        optional.extend(expense_documents["optional"])

    def _needs_farm_documents(self, answers: Dict[str, Any]) -> bool:
        """Determine if farm documents are needed"""
        try:
            return (
                answers.get("has_farm_income", False) or
                answers.get("has_agricultural_payments", False) or
                answers.get("has_farm_expenses", False)
            )
        except Exception as exception:
            self.logger.error(f"Error checking farm documents: {str(exception)}")
            return False
            
    def _get_farm_requirements(self, answers: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Get farm document requirements"""
        required = []
        optional = []

        # Add Schedule F requirements
        if answers.get("has_farm_income"):
            schedule_f = self.schedule_requirements["SCHEDULE_F"]
            required.extend(schedule_f["required"])
            optional.extend(schedule_f.get("optional", []))

        # Add agricultural payment documentation
        if answers.get("has_agricultural_payments"):
            required.append({
                "type": "AGRICULTURAL_PAYMENTS",
                "priority": "high",
                "metadata": {
                    "retention_years": 7,
                    "requires_program_details": True
                }
            })

        # Add crop insurance documentation
        if answers.get("has_crop_insurance"):
            required.append({
                "type": "CROP_INSURANCE",
                "priority": "high",
                "metadata": {
                    "retention_years": 7,
                    "requires_policy_details": True
                }
            })

        return {"required": required, "optional": optional}
