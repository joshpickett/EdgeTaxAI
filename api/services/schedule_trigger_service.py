from typing import Dict, Any, List
import logging
from decimal import Decimal
from api.models.tax_forms import TaxForms, FormType
from api.services.mef.schedule_management_service import ScheduleManagementService


class ScheduleTriggerService:
    """Service for managing schedule triggers and qualifications"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.schedule_manager = ScheduleManagementService()

        # Define trigger thresholds
        self.thresholds = {
            "schedule_c": Decimal("400"),  # Self-employment income threshold
            "schedule_se": Decimal("400"),  # Self-employment tax threshold
            "schedule_e": Decimal("0"),  # Any rental income
            "form_8829": {"min_area": 0, "exclusive_use": True},  # Any dedicated space
        }

    async def analyze_schedule_requirements(
        self, user_id: int, tax_year: int
    ) -> Dict[str, Any]:
        """Analyze which schedules are required based on tax data"""
        try:
            tax_data = await self._get_tax_data(user_id, tax_year)

            required_schedules = []
            warnings = []

            # Check Schedule C requirement
            if self._needs_schedule_c(tax_data):
                required_schedules.append("SCHEDULE_C")

                # Check Schedule SE if Schedule C is required
                if self._needs_schedule_se(tax_data):
                    required_schedules.append("SCHEDULE_SE")

                # Check Form 8829 if home office is claimed
                if self._qualifies_for_8829(tax_data):
                    required_schedules.append("FORM_8829")

            # Check Schedule E requirement
            if self._needs_schedule_e(tax_data):
                required_schedules.append("SCHEDULE_E")

            return {
                "required_schedules": required_schedules,
                "warnings": warnings,
                "analysis": self._generate_analysis(tax_data, required_schedules),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing schedule requirements: {str(e)}")
            raise

    def _needs_schedule_c(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Schedule C is needed"""
        self_employment_income = Decimal(
            str(tax_data.get("income_sources", {}).get("self_employment", 0))
        )
        return self_employment_income > self.thresholds["schedule_c"]

    def _needs_schedule_se(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Schedule SE is needed"""
        net_earnings = Decimal(
            str(tax_data.get("income_sources", {}).get("net_earnings", 0))
        )
        return net_earnings > self.thresholds["schedule_se"]

    def _needs_schedule_e(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Schedule E is needed"""
        rental_income = Decimal(
            str(tax_data.get("income_sources", {}).get("rental", 0))
        )
        return rental_income > self.thresholds["schedule_e"]

    def _qualifies_for_8829(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Form 8829 (Home Office) is qualified"""
        home_office = tax_data.get("home_office", {})

        if not home_office:
            return False

        area_used = Decimal(str(home_office.get("area_used", 0)))
        exclusive_use = home_office.get("exclusive_use", False)

        return (
            area_used > self.thresholds["form_8829"]["min_area"]
            and exclusive_use == self.thresholds["form_8829"]["exclusive_use"]
        )

    def _generate_analysis(
        self, tax_data: Dict[str, Any], required_schedules: List[str]
    ) -> Dict[str, Any]:
        """Generate detailed analysis of schedule requirements"""
        analysis = {}

        if "SCHEDULE_C" in required_schedules:
            analysis["schedule_c"] = {
                "reason": "Self-employment income exceeds threshold",
                "income": tax_data.get("income_sources", {}).get("self_employment", 0),
            }

        if "SCHEDULE_SE" in required_schedules:
            analysis["schedule_se"] = {
                "reason": "Net earnings require self-employment tax",
                "net_earnings": tax_data.get("income_sources", {}).get(
                    "net_earnings", 0
                ),
            }

        if "FORM_8829" in required_schedules:
            analysis["form_8829"] = {
                "reason": "Qualified home office expenses claimed",
                "area_used": tax_data.get("home_office", {}).get("area_used", 0),
            }

        return analysis

    async def _get_tax_data(self, user_id: int, tax_year: int) -> Dict[str, Any]:
        """Get tax data for analysis"""
        # Implementation would fetch actual tax data
        # This is a placeholder
        return {
            "income_sources": {
                "self_employment": 5000,
                "net_earnings": 4500,
                "rental": 0,
            },
            "home_office": {"area_used": 200, "exclusive_use": True},
        }
