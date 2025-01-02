from typing import Dict, Any, List
import logging
from datetime import datetime
from decimal import Decimal
from api.services.category.category_manager import CategoryManager
from api.services.error_handling_service import ErrorHandlingService


class ValidationManager:
    """Service for managing document validation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.category_manager = CategoryManager()
        self.error_service = ErrorHandlingService()
        self.farm_validation_rules = self._initialize_farm_rules()
        self.form_validation_rules = self._initialize_form_validation_rules()

        # Define quality scoring weights
        self.quality_weights = {"completeness": 0.4, "clarity": 0.3, "compliance": 0.3}

    async def validate_document(
        self, document: Dict[str, Any], category: str
    ) -> Dict[str, Any]:
        """Validate document and calculate quality score"""
        try:
            start_time = datetime.utcnow()
            # Validate against category rules
            category_validation = self.category_manager.validate_category(
                category, document
            )

            # Calculate quality score
            quality_score = self._calculate_quality_score(document, category)

            # Check cross-category validation rules
            cross_validation = await self._validate_cross_category(document, category)

            # Log performance metrics
            await self.performance_logger.log_metrics(
                {
                    "operation": "validate_document",
                    "duration": (datetime.utcnow() - start_time).total_seconds(),
                    "category": category,
                }
            )

            validation_result = {
                "is_valid": category_validation["is_valid"]
                and cross_validation["is_valid"],
                "quality_score": quality_score,
                "errors": [
                    *category_validation.get("errors", []),
                    *cross_validation.get("errors", []),
                ],
                "warnings": [
                    *category_validation.get("warnings", []),
                    *cross_validation.get("warnings", []),
                ],
                "deadline_status": await self._check_deadlines(document, category),
            }

            # Handle validation errors if any
            if not validation_result["is_valid"]:
                await self.error_service.handle_error(
                    Exception("Validation failed"),
                    {
                        "document_id": document.get("id"),
                        "category": category,
                        "errors": validation_result["errors"],
                    },
                    "VALIDATION",
                )

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating document: {str(e)}")
            raise

    def _initialize_farm_rules(self) -> Dict[str, Any]:
        """Initialize farm-specific validation rules"""
        return {
            "SCHEDULE_F": {
                "required_fields": [
                    "farm_name",
                    "ein",
                    "farm_address",
                    "principal_product"
                ],
                "validation_rules": [
                    "farm_income_validation",
                    "expense_validation",
                    "inventory_validation"
                ],
                "thresholds": {
                    "inventory_change": Decimal("500000")
                }
            },
            "AGRICULTURAL_PAYMENTS": {
                "required_fields": [
                    "program_name",
                    "payment_amount",
                    "payment_date"
                ],
                "validation_rules": ["payment_validation"]
            }
        }

    def _initialize_form_validation_rules(self) -> Dict[str, Any]:
        """Initialize validation rules for all forms"""
        return {
            "STATE_CREDIT": {
                "required_fields": ["state_code", "credit_type", "amount"],
                "validation_rules": ["state_credit_validation"]
            },
            "FORM_1098T": {
                "required_fields": ["institution_name", "student_name", "tuition_amount"],
                "validation_rules": ["education_expense_validation"]
            },
            "FORM_1040": {
                "required_fields": ["taxpayer_info", "income", "deductions", "tax_calculation"],
                "validation_rules": ["income_validation", "deduction_validation"]
            },
            "SCHEDULE_A": {
                "required_fields": ["itemized_deductions", "total_deductions"],
                "validation_rules": ["deduction_threshold_validation"]
            },
            "SCHEDULE_B": {
                "required_fields": ["interest_income", "dividend_income"],
                "validation_rules": ["interest_threshold_validation"]
            },
            "SCHEDULE_C": {
                "required_fields": ["business_income", "business_expenses"],
                "validation_rules": ["business_income_validation"]
            },
            "SCHEDULE_D": {
                "required_fields": ["capital_gains", "capital_losses"],
                "validation_rules": ["capital_gains_validation"]
            },
            "SCHEDULE_E": {
                "required_fields": ["rental_income", "rental_expenses"],
                "validation_rules": ["rental_income_validation"]
            },
            "SCHEDULE_F": {
                "required_fields": ["farm_income", "farm_expenses"],
                "validation_rules": ["farm_income_validation"]
            },
            "FORM_2555": {
                "required_fields": ["foreign_earned_income", "foreign_housing"],
                "validation_rules": ["foreign_income_validation"]
            },
            "FORM_8938": {
                "required_fields": ["foreign_assets", "asset_value"],
                "validation_rules": ["foreign_asset_threshold_validation"]
            },
            "FORM_8283": {
                "required_fields": ["donation_description", "donation_value"],
                "validation_rules": ["donation_threshold_validation"]
            },
            "FORM_4684": {
                "required_fields": ["casualty_description", "loss_amount"],
                "validation_rules": ["casualty_loss_validation"]
            },
            "FORM_5695": {
                "required_fields": ["energy_improvements", "cost"],
                "validation_rules": ["energy_credit_validation"]
            },
            "FORM_8863": {
                "required_fields": ["education_expenses", "institution_info"],
                "validation_rules": ["education_credit_validation"]
            },
            "FORM_2441": {
                "required_fields": ["care_provider", "care_expenses"],
                "validation_rules": ["child_care_validation"]
            },
            "FORM_5329": {
                "required_fields": ["distribution_amount", "reason"],
                "validation_rules": ["early_withdrawal_validation"]
            },
            "FORM_8606": {
                "required_fields": ["ira_basis", "distribution"],
                "validation_rules": ["ira_contribution_validation"]
            },
            "FORM_3520": {
                "required_fields": ["gift_description", "gift_value"],
                "validation_rules": ["foreign_gift_validation"]
            },
            "FORM_4562": {
                "required_fields": ["asset_description", "depreciation_method"],
                "validation_rules": ["depreciation_validation"]
            },
            "FORM_8829": {
                "required_fields": ["home_expenses", "business_percentage"],
                "validation_rules": ["home_office_validation"]
            },
            "FORM_1116": {
                "required_fields": ["foreign_tax_paid", "foreign_income"],
                "validation_rules": ["foreign_tax_credit_validation"]
            },
            "FBAR": {
                "required_fields": ["account_info", "maximum_value"],
                "validation_rules": ["fbar_threshold_validation"]
            }
        }

    def _calculate_quality_score(
        self, document: Dict[str, Any], category: str
    ) -> float:
        """Calculate document quality score"""
        try:
            scores = {
                "completeness": self._calculate_completeness(document, category),
                "clarity": self._calculate_clarity(document),
                "compliance": self._calculate_compliance(document, category),
            }

            weighted_score = sum(
                scores[metric] * self.quality_weights[metric] for metric in scores
            )

            return round(weighted_score, 2)

        except Exception as e:
            self.logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0

    async def _validate_cross_category(
        self, document: Dict[str, Any], category: str
    ) -> Dict[str, Any]:
        """Validate cross-category rules"""
        try:
            validation_result = {"is_valid": True, "errors": [], "warnings": []}

            # Get related categories
            related_categories = self.category_manager.get_related_categories(category)

            # Check cross-category rules
            for related_category in related_categories:
                related_validation = await self._check_related_category(
                    document, category, related_category
                )

                if not related_validation["is_valid"]:
                    validation_result["is_valid"] = False
                    validation_result["errors"].extend(related_validation["errors"])
                    validation_result["warnings"].extend(related_validation["warnings"])

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating cross-category rules: {str(e)}")
            raise

    def _check_deadlines(
        self, document: Dict[str, Any], category: str
    ) -> Dict[str, Any]:
        """Check document deadlines"""
        try:
            metadata = self.category_manager.get_category_metadata(category)
            deadlines = metadata.get("deadlines", {})

            current_date = datetime.utcnow()
            deadline_status = {
                "has_deadlines": bool(deadlines),
                "upcoming_deadlines": [],
                "overdue_deadlines": [],
            }

            for deadline_type, deadline_date in deadlines.items():
                deadline = datetime.fromisoformat(deadline_date)
                if deadline < current_date:
                    deadline_status["overdue_deadlines"].append(
                        {"type": deadline_type, "deadline": deadline_date}
                    )
                else:
                    deadline_status["upcoming_deadlines"].append(
                        {"type": deadline_type, "deadline": deadline_date}
                    )

            return deadline_status

        except Exception as e:
            self.logger.error(f"Error checking deadlines: {str(e)}")
            return {"has_deadlines": False}

    def _calculate_completeness(self, document: Dict[str, Any], category: str) -> float:
        """Calculate document completeness score"""
        try:
            required_fields = self.category_manager.get_category_rules(category).get(
                "required_fields", []
            )
            if not required_fields:
                return 1.0

            present_fields = sum(1 for field in required_fields if field in document)
            return present_fields / len(required_fields)

        except Exception as e:
            self.logger.error(f"Error calculating completeness: {str(e)}")
            return 0.0

    def _calculate_clarity(self, document: Dict[str, Any]) -> float:
        """Calculate document clarity score"""
        # Implementation would include image quality checks, OCR confidence scores, etc.
        return 1.0

    def _calculate_compliance(self, document: Dict[str, Any], category: str) -> float:
        """Calculate compliance score"""
        try:
            rules = self.category_manager.get_category_rules(category)
            total_rules = len(rules)
            if not total_rules:
                return 1.0

            passed_rules = sum(1 for rule in rules if self._check_rule(document, rule))
            return passed_rules / total_rules

        except Exception as e:
            self.logger.error(f"Error calculating compliance: {str(e)}")
            return 0.0

    def _check_rule(self, document: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if document passes a specific rule"""
        rule_type = rule.get("type")
        if rule_type == "required_fields":
            return all(field in document for field in rule["fields"])
        elif rule_type == "format_checks":
            return all(
                self._check_format(document, format_check)
                for format_check in rule["formats"]
            )
        return True

    async def _check_related_category(
        self, document: Dict[str, Any], category: str, related_category: str
    ) -> Dict[str, Any]:
        """Check validation rules between related categories"""
        # Implementation would check relationships between categories
        return {"is_valid": True, "errors": [], "warnings": []}

    async def validate_farm_document(
        self, document: Dict[str, Any], document_type: str
    ) -> Dict[str, Any]:
        """Validate farm-specific document"""
        try:
            rules = self.farm_validation_rules.get(document_type, {})
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }

            # Validate required fields
            for field in rules.get("required_fields", []):
                if field not in document:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating farm document: {str(e)}")
            return {"is_valid": False, "errors": [str(e)], "warnings": []}

    async def validate_form(self, form_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate specific form data"""
        try:
            rules = self.form_validation_rules.get(form_type, {})
            return await self._validate_against_rules(data, rules)
        except Exception as e:
            self.logger.error(f"Error validating form {form_type}: {str(e)}")
            raise
