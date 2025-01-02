from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.validation.validation_manager import ValidationManager


class DocumentRequirementConditions:
    """Service for handling conditional document requirements"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_manager = ValidationManager()
        self.form_conditions = self._initialize_form_conditions()

    def evaluate_conditions(
        self, conditions: Dict[str, Any], user_answers: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate conditions and return required documents"""
        try:
            required_documents = []

            for condition_key, condition_data in conditions.items():
                trigger = condition_data.get("trigger")
                if self._evaluate_trigger(trigger, user_answers):
                    required_documents.extend(condition_data.get("required_docs", []))

            return required_documents

        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {str(e)}")
            raise

    def _evaluate_trigger(self, trigger: str, answers: Dict[str, Any]) -> bool:
        """Evaluate trigger condition"""
        try:
            if not trigger:
                return False

            # Parse trigger condition
            field, operator, value = self._parse_trigger(trigger)

            # Get actual value from answers
            actual_value = answers.get(field)

            # Evaluate condition
            if operator == "==":
                return str(actual_value).lower() == str(value).lower()
            elif operator == "!=":
                return str(actual_value).lower() != str(value).lower()
            elif operator == ">":
                return float(actual_value) > float(value)
            elif operator == "<":
                return float(actual_value) < float(value)

            return False

        except Exception as e:
            self.logger.error(f"Error evaluating trigger: {str(e)}")
            return False

    def _parse_trigger(self, trigger: str) -> tuple:
        """Parse trigger string into components"""
        try:
            # Remove whitespace
            trigger = trigger.replace(" ", "")

            # Find operator
            operators = ["==", "!=", ">", "<"]
            used_operator = None

            for operator in operators:
                if operator in trigger:
                    used_operator = operator
                    break

            if not used_operator:
                raise ValueError(f"Invalid trigger format: {trigger}")

            # Split into field and value
            field, value = trigger.split(used_operator)

            # Clean up value
            value = value.strip("\"'")

            return field, used_operator, value

        except Exception as e:
            self.logger.error(f"Error parsing trigger: {str(e)}")
            raise

    def validate_conditions(self, conditions: Dict[str, Any]) -> List[str]:
        """Validate condition format"""
        errors = []

        for condition_key, condition_data in conditions.items():
            if not isinstance(condition_data, dict):
                errors.append(f"Invalid condition format for {condition_key}")
                continue

            if "trigger" not in condition_data:
                errors.append(f"Missing trigger for condition {condition_key}")

            if "required_docs" not in condition_data:
                errors.append(f"Missing required_docs for condition {condition_key}")

            if not isinstance(condition_data.get("required_docs", []), list):
                errors.append(f"Invalid required_docs format for {condition_key}")

        return errors

    def _initialize_form_conditions(self) -> Dict[str, Any]:
        """Initialize form-specific conditions"""
        return {
            "FORM_1098T": {
                "trigger": "has_education_expenses == true",
                "dependencies": ["EDUCATION_EXPENSES", "INSTITUTION_INFO"]
            },
            "STATE_CREDIT": {
                "trigger": "has_state_credits == true",
                "dependencies": ["STATE_TAX_DOCUMENTS"]
            },
            "STATEMENT": {
                "trigger": "requires_supporting_documentation == true",
                "dependencies": ["SUPPORTING_DOCUMENTS"]
            },
            "FORM_1040": {
                "required": True,
                "dependencies": ["W2", "1099_NEC", "1099_K"]
            },
            "SCHEDULE_A": {
                "trigger": "itemized_deductions > standard_deduction",
                "dependencies": ["CHARITABLE_CONTRIBUTIONS", "MORTGAGE_INTEREST"]
            },
            "SCHEDULE_B": {
                "trigger": "interest_income > 1500 or dividend_income > 1500",
                "dependencies": ["1099_INT", "1099_DIV"]
            },
            "SCHEDULE_C": {
                "trigger": "has_self_employment == true",
                "dependencies": ["1099_NEC", "1099_K", "BUSINESS_EXPENSES"]
            },
            "SCHEDULE_D": {
                "trigger": "has_investment_sales == true",
                "dependencies": ["1099_B"]
            },
            "SCHEDULE_E": {
                "trigger": "has_rental_income == true",
                "dependencies": ["RENTAL_INCOME", "PROPERTY_EXPENSES"]
            },
            "SCHEDULE_F": {
                "trigger": "has_farm_income == true",
                "dependencies": ["FARM_INCOME", "AGRICULTURAL_PAYMENTS"]
            },
            "FORM_2555": {
                "trigger": "has_foreign_income == true",
                "dependencies": ["FOREIGN_INCOME_DOCUMENTATION"]
            },
            "FORM_8938": {
                "trigger": "foreign_assets_value >= 50000",
                "dependencies": ["FOREIGN_ACCOUNT_STATEMENTS"]
            },
            "FORM_8283": {
                "trigger": "noncash_donations_value >= 500",
                "dependencies": ["DONATION_DOCUMENTATION"]
            },
            "FORM_4684": {
                "trigger": "has_casualty_loss == true",
                "dependencies": ["LOSS_DOCUMENTATION"]
            },
            "FORM_5695": {
                "trigger": "has_energy_improvements == true",
                "dependencies": ["ENERGY_IMPROVEMENT_RECEIPTS"]
            },
            "FORM_8863": {
                "trigger": "has_education_expenses == true",
                "dependencies": ["1098_T"]
            },
            "FORM_2441": {
                "trigger": "has_child_care == true",
                "dependencies": ["CARE_PROVIDER_DOCUMENTATION"]
            },
            "FORM_5329": {
                "trigger": "has_early_withdrawal == true",
                "dependencies": ["1099_R"]
            },
            "FORM_8606": {
                "trigger": "has_nondeductible_ira == true",
                "dependencies": ["IRA_CONTRIBUTION_STATEMENTS"]
            },
            "FORM_3520": {
                "trigger": "has_foreign_gifts == true",
                "dependencies": ["FOREIGN_GIFT_DOCUMENTATION"]
            },
            "FORM_4562": {
                "trigger": "has_depreciable_assets == true",
                "dependencies": ["ASSET_PURCHASE_RECORDS"]
            },
            "FORM_8829": {
                "trigger": "has_home_office == true",
                "dependencies": ["HOME_OFFICE_DOCUMENTATION"]
            },
            "FORM_1116": {
                "trigger": "has_foreign_tax_paid == true",
                "dependencies": ["FOREIGN_TAX_DOCUMENTATION"]
            },
            "FBAR": {
                "trigger": "foreign_accounts_value >= 10000",
                "dependencies": ["FOREIGN_BANK_STATEMENTS"]
            }
        }

    async def validate_form_requirements(self, form_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate form-specific requirements"""
        try:
            form_conditions = self.form_conditions.get(form_type, {})
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }

            # Validate dependencies
            for dependency in form_conditions.get("dependencies", []):
                if not self._check_dependency(dependency, data):
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required dependency: {dependency}")

            return validation_result
        except Exception as e:
            self.logger.error(f"Error validating form requirements: {str(e)}")
            raise
