from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.error_handling_service import ErrorHandlingService
from api.services.mef.validation_rules import ValidationRules


class RealTimeValidator:
    """Service for real-time form validation"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_service = ErrorHandlingService()
        self.validation_rules = ValidationRules()

    async def validate_field(
        self,
        form_type: str,
        field_name: str,
        value: Any,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Validate individual field in real-time"""
        try:
            # Get field rules
            rules = self.validation_rules.get_field_rules(form_type, field_name)

            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": [],
            }

            # Apply each rule
            for rule in rules:
                result = await self._apply_rule(rule, value, context)
                if not result["is_valid"]:
                    validation_result["is_valid"] = False
                    validation_result["errors"].extend(result["errors"])
                    validation_result["warnings"].extend(result["warnings"])
                    validation_result["suggestions"].extend(
                        self._generate_suggestions(result)
                    )

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating field: {str(e)}")
            raise

    async def validate_section(
        self, form_type: str, section: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate form section in real-time"""
        try:
            validation_results = {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "suggestions": [],
            }

            # Validate each field in section
            for field_name, value in data.items():
                field_result = await self.validate_field(
                    form_type, field_name, value, data
                )

                if not field_result["is_valid"]:
                    validation_results["is_valid"] = False
                    validation_results["errors"].extend(field_result["errors"])
                    validation_results["warnings"].extend(field_result["warnings"])
                    validation_results["suggestions"].extend(
                        field_result["suggestions"]
                    )

            # Validate section-level rules
            section_result = await self._validate_section_rules(
                form_type, section, data
            )

            if not section_result["is_valid"]:
                validation_results["is_valid"] = False
                validation_results["errors"].extend(section_result["errors"])
                validation_results["warnings"].extend(section_result["warnings"])
                validation_results["suggestions"].extend(section_result["suggestions"])

            return validation_results

        except Exception as e:
            self.logger.error(f"Error validating section: {str(e)}")
            raise

    async def _apply_rule(
        self, rule: Dict[str, Any], value: Any, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Apply validation rule to value"""
        try:
            rule_type = rule["type"]
            rule_params = rule.get("params", {})

            if rule_type == "required":
                return self._validate_required(value)
            elif rule_type == "format":
                return self._validate_format(value, rule_params)
            elif rule_type == "range":
                return self._validate_range(value, rule_params)
            elif rule_type == "dependency":
                return self._validate_dependency(value, context, rule_params)
            else:
                return {"is_valid": True, "errors": [], "warnings": []}

        except Exception as e:
            self.logger.error(f"Error applying rule: {str(e)}")
            raise

    def _validate_required(self, value: Any) -> Dict[str, Any]:
        """Validate required field"""
        is_valid = value is not None and value != ""
        return {
            "is_valid": is_valid,
            "errors": (
                []
                if is_valid
                else [{"type": "required", "message": "This field is required"}]
            ),
            "warnings": [],
        }

    def _validate_format(self, value: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate field format"""
        import re

        pattern = params.get("pattern")
        if not pattern or not value:
            return {"is_valid": True, "errors": [], "warnings": []}

        is_valid = bool(re.match(pattern, str(value)))
        return {
            "is_valid": is_valid,
            "errors": (
                []
                if is_valid
                else [
                    {
                        "type": "format",
                        "message": params.get("message", "Invalid format"),
                    }
                ]
            ),
            "warnings": [],
        }

    def _validate_range(self, value: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate value range"""
        if not value:
            return {"is_valid": True, "errors": [], "warnings": []}

        min_val = params.get("min")
        max_val = params.get("max")

        is_valid = True
        errors = []

        if min_val is not None and value < min_val:
            is_valid = False
            errors.append(
                {"type": "range", "message": f"Value must be at least {min_val}"}
            )

        if max_val is not None and value > max_val:
            is_valid = False
            errors.append(
                {"type": "range", "message": f"Value must not exceed {max_val}"}
            )

        return {"is_valid": is_valid, "errors": errors, "warnings": []}

    def _validate_dependency(
        self, value: Any, context: Dict[str, Any], params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate field dependencies"""
        if not context:
            return {"is_valid": True, "errors": [], "warnings": []}

        dependent_field = params.get("field")
        dependent_value = context.get(dependent_field)

        if params.get("required") and dependent_value and not value:
            return {
                "is_valid": False,
                "errors": [
                    {
                        "type": "dependency",
                        "message": f"This field is required when {dependent_field} is provided",
                    }
                ],
                "warnings": [],
            }

        return {"is_valid": True, "errors": [], "warnings": []}

    def _generate_suggestions(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate helpful suggestions based on validation results"""
        suggestions = []

        for error in validation_result.get("errors", []):
            suggestions.append(self._get_suggestion_for_error(error))

        return suggestions

    def _get_suggestion_for_error(self, error: Dict[str, Any]) -> str:
        """Get specific suggestion for error type"""
        suggestion_map = {
            "required": "This field is required for IRS compliance",
            "format": "Please check the format and try again",
            "range": "The value entered is outside acceptable range",
            "dependency": "This field is required based on other information provided",
        }
        return suggestion_map.get(error["type"], "Please verify this field")
