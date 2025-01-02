from typing import Dict, Any, List
import logging
from api.models.tax_forms import TaxForms, FormType
from api.services.mef.validation_rules import ValidationRules


class ScheduleAttachmentManager:
    """Manages schedule attachments and dependencies for tax forms"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ValidationRules()

        # Define schedule dependencies
        self.dependencies = {
            "SCHEDULE_C": ["1040"],
            "SCHEDULE_SE": ["1040", "SCHEDULE_C"],
            "SCHEDULE_A": ["1040"],
            "SCHEDULE_B": ["1040"],
            "SCHEDULE_D": ["1040"],
            "SCHEDULE_E": ["1040"],
        }

    def validate_attachments(
        self, form_type: str, attachments: List[str]
    ) -> Dict[str, Any]:
        """Validate schedule attachments for a given form"""
        try:
            required_schedules = self.get_required_schedules(form_type)
            missing_schedules = [
                schedule
                for schedule in required_schedules
                if schedule not in attachments
            ]

            invalid_attachments = [
                attachment
                for attachment in attachments
                if not self._is_valid_attachment(form_type, attachment)
            ]

            return {
                "is_valid": not (missing_schedules or invalid_attachments),
                "missing_schedules": missing_schedules,
                "invalid_attachments": invalid_attachments,
            }

        except Exception as e:
            self.logger.error(f"Error validating attachments: {str(e)}")
            raise

    def get_required_schedules(self, form_type: str) -> List[str]:
        """Get required schedules for a form type"""
        required = []

        # Check form-specific requirements
        if form_type == "1040":
            if self._has_self_employment_income():
                required.append("SCHEDULE_C")
                required.append("SCHEDULE_SE")
            if self._has_itemized_deductions():
                required.append("SCHEDULE_A")
            if self._has_investment_income():
                required.append("SCHEDULE_B")
            if self._has_capital_gains():
                required.append("SCHEDULE_D")

        return required

    def resolve_dependencies(self, schedules: List[str]) -> List[str]:
        """Resolve schedule dependencies and return ordered list"""
        resolved = []
        visited = set()

        def visit(schedule):
            if schedule in visited:
                return
            visited.add(schedule)

            # Process dependencies first
            for dep in self.dependencies.get(schedule, []):
                visit(dep)
            resolved.append(schedule)

        for schedule in schedules:
            visit(schedule)

        return resolved

    def _is_valid_attachment(self, form_type: str, attachment: str) -> bool:
        """Check if attachment is valid for form type"""
        valid_attachments = {
            "1040": [
                "SCHEDULE_A",
                "SCHEDULE_B",
                "SCHEDULE_C",
                "SCHEDULE_D",
                "SCHEDULE_E",
                "SCHEDULE_SE",
            ],
            "1040EZ": [],  # 1040EZ doesn't support schedules
            "1099NEC": [],
            "1099K": [],
        }
        return attachment in valid_attachments.get(form_type, [])

    def _has_self_employment_income(self) -> bool:
        """Check if taxpayer has self-employment income"""
        # Implementation would check actual income data
        return True

    def _has_itemized_deductions(self) -> bool:
        """Check if taxpayer has itemized deductions"""
        # Implementation would check deduction data
        return True

    def _has_investment_income(self) -> bool:
        """Check if taxpayer has investment income"""
        # Implementation would check investment income data
        return True

    def _has_capital_gains(self) -> bool:
        """Check if taxpayer has capital gains"""
        # Implementation would check capital gains data
        return True
