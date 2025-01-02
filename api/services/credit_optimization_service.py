from typing import Dict, Any, List
import logging
from decimal import Decimal
from datetime import datetime
from api.models.credits import Credits
from api.utils.ai_utils import AITransactionAnalyzer


class CreditOptimizationService:
    """Service for optimizing tax credits"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = AITransactionAnalyzer()

        self.credit_categories = {
            "child_tax_credit": {
                "max_amount": Decimal("2000.00"),
                "income_limit": Decimal("200000.00"),
                "required_documents": ["birth_certificate", "social_security_card"],
            },
            "earned_income_credit": {
                "max_amount": Decimal("6935.00"),
                "income_limits": {
                    "single": Decimal("51567.00"),
                    "married": Decimal("57414.00"),
                },
                "required_documents": ["w2", "income_verification"],
            },
            "education_credits": {
                "american_opportunity": {
                    "max_amount": Decimal("2500.00"),
                    "income_limit": Decimal("90000.00"),
                    "required_documents": ["1098-T", "education_expenses"],
                },
                "lifetime_learning": {
                    "max_amount": Decimal("2000.00"),
                    "income_limit": Decimal("69000.00"),
                    "required_documents": ["1098-T", "education_expenses"],
                },
            },
        }

    async def analyze_credit_opportunities(
        self, user_id: int, tax_year: int
    ) -> Dict[str, Any]:
        """Analyze and optimize credit opportunities"""
        try:
            # Get user's tax data
            tax_data = await self._get_user_tax_data(user_id, tax_year)
            existing_credits = await self._get_existing_credits(user_id, tax_year)

            # Analyze potential credits
            opportunities = []
            for category in self.credit_categories:
                analysis = await self._analyze_credit_category(category, tax_data)
                if analysis["eligible"]:
                    opportunities.append(analysis)

            # Calculate potential savings
            total_potential = sum(op["potential_amount"] for op in opportunities)
            current_credits = sum(c.amount for c in existing_credits)

            return {
                "opportunities": opportunities,
                "total_potential": total_potential,
                "current_credits": current_credits,
                "additional_savings": total_potential - current_credits,
                "recommendations": self._generate_recommendations(opportunities),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing credit opportunities: {str(e)}")
            raise

    async def _analyze_credit_category(
        self, category: str, tax_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze specific credit category"""
        try:
            credit_info = self.credit_categories[category]

            # Check eligibility
            eligible = await self._check_eligibility(category, tax_data, credit_info)

            if not eligible:
                return {
                    "category": category,
                    "eligible": False,
                    "reason": "Income exceeds limit or missing requirements",
                }

            # Calculate potential credit amount
            potential_amount = await self._calculate_credit_amount(
                category, tax_data, credit_info
            )

            # Check documentation requirements
            missing_documents = await self._check_documentation(
                category, tax_data, credit_info
            )

            return {
                "category": category,
                "eligible": True,
                "potential_amount": potential_amount,
                "missing_documentation": missing_documents,
                "requirements": credit_info.get("required_documents", []),
            }

        except Exception as e:
            self.logger.error(f"Error analyzing credit category: {str(e)}")
            raise

    async def _check_eligibility(
        self, category: str, tax_data: Dict[str, Any], credit_info: Dict[str, Any]
    ) -> bool:
        """Check eligibility for specific credit"""
        try:
            income = Decimal(str(tax_data.get("adjusted_gross_income", 0)))

            # Check income limits
            if "income_limit" in credit_info:
                if income > credit_info["income_limit"]:
                    return False
            elif "income_limits" in credit_info:
                limit = credit_info["income_limits"].get(
                    tax_data.get("filing_status", "single")
                )
                if income > limit:
                    return False

            # Check specific requirements
            if category == "child_tax_credit":
                if not tax_data.get("qualifying_children", 0):
                    return False
            elif category == "earned_income_credit":
                if not tax_data.get("earned_income", 0):
                    return False
            elif category == "education_credits":
                if not tax_data.get("education_expenses", 0):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking credit eligibility: {str(e)}")
            raise

    def _generate_recommendations(
        self, opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on opportunities"""
        recommendations = []

        for opportunity in opportunities:
            category = opportunity["category"]
            missing_documents = opportunity.get("missing_documentation", [])

            recommendation = {
                "category": category,
                "potential_amount": opportunity["potential_amount"],
                "action_items": self._get_action_items(category, missing_documents),
                "documentation_needed": missing_documents,
            }

            recommendations.append(recommendation)

        return recommendations

    def _get_action_items(
        self, category: str, missing_documents: List[str]
    ) -> List[str]:
        """Generate specific action items for a category"""
        action_items = []

        if category == "child_tax_credit":
            action_items.extend(
                [
                    "Gather birth certificates for qualifying children",
                    "Collect social security cards for qualifying children",
                    "Document child residency for the tax year",
                ]
            )
        elif category == "earned_income_credit":
            action_items.extend(
                [
                    "Collect all W-2 forms",
                    "Document self-employment income",
                    "Verify income eligibility",
                ]
            )
        elif category == "education_credits":
            action_items.extend(
                [
                    "Gather Form 1098-T from educational institutions",
                    "Collect receipts for qualified education expenses",
                    "Document course enrollment and degree program",
                ]
            )

        # Add specific items for missing documentation
        for document in missing_documents:
            action_items.append(f"Obtain missing document: {document}")

        return action_items
