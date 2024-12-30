from typing import Dict, Any, List
import logging
from decimal import Decimal
from datetime import datetime
from api.models.deductions import Deductions
from api.utils.ai_utils import AITransactionAnalyzer

class DeductionOptimizationService:
    """Service for optimizing tax deductions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = AITransactionAnalyzer()
        
        self.deduction_categories = {
            'vehicle': {
                'standard_rate': Decimal('0.655'),  # 2023 IRS mileage rate
                'documentation_required': ['mileage_log', 'vehicle_expenses']
            },
            'home_office': {
                'calculation_methods': ['standard', 'actual'],
                'required_fields': ['square_footage', 'total_home_square_footage']
            },
            'supplies': {
                'documentation_required': ['receipts'],
                'threshold': Decimal('2500')  # De minimis safe harbor threshold
            },
            'travel': {
                'documentation_required': ['receipts', 'business_purpose'],
                'meal_percentage': Decimal('0.50')  # 50% meal deduction
            }
        }

    async def analyze_deduction_opportunities(
        self,
        user_id: int,
        year: int
    ) -> Dict[str, Any]:
        """Analyze and optimize deduction opportunities"""
        try:
            # Get all expenses and existing deductions
            expenses = await self._get_user_expenses(user_id, year)
            existing_deductions = await self._get_existing_deductions(user_id, year)
            
            # Analyze each expense for deduction potential
            opportunities = []
            for expense in expenses:
                analysis = await self._analyze_expense(expense)
                if analysis['deduction_potential'] > 0:
                    opportunities.append(analysis)
            
            # Calculate potential savings
            total_potential = sum(op['deduction_potential'] for op in opportunities)
            current_deductions = sum(d.amount for d in existing_deductions)
            
            return {
                'opportunities': opportunities,
                'total_potential': total_potential,
                'current_deductions': current_deductions,
                'additional_savings': total_potential - current_deductions,
                'recommendations': self._generate_recommendations(opportunities)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing deduction opportunities: {str(e)}")
            raise

    async def optimize_vehicle_deductions(
        self,
        user_id: int,
        year: int
    ) -> Dict[str, Any]:
        """Optimize vehicle-related deductions"""
        try:
            # Get mileage and vehicle expenses
            mileage = await self._get_mileage_records(user_id, year)
            vehicle_expenses = await self._get_vehicle_expenses(user_id, year)
            
            # Calculate standard mileage deduction
            standard_deduction = self._calculate_standard_mileage(mileage)
            
            # Calculate actual expenses deduction
            actual_deduction = self._calculate_actual_vehicle_expenses(vehicle_expenses)
            
            # Compare and recommend best method
            if standard_deduction > actual_deduction:
                recommendation = {
                    'method': 'standard',
                    'amount': standard_deduction,
                    'explanation': 'Standard mileage rate provides higher deduction'
                }
            else:
                recommendation = {
                    'method': 'actual',
                    'amount': actual_deduction,
                    'explanation': 'Actual expense method provides higher deduction'
                }
                
            return {
                'standard_deduction': standard_deduction,
                'actual_deduction': actual_deduction,
                'recommendation': recommendation
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing vehicle deductions: {str(e)}")
            raise

    async def optimize_home_office_deduction(
        self,
        user_id: int,
        year: int
    ) -> Dict[str, Any]:
        """Optimize home office deduction"""
        try:
            # Get home office data
            home_office_data = await self._get_home_office_data(user_id, year)
            
            # Calculate simplified method
            simplified_deduction = self._calculate_simplified_home_office(
                home_office_data['office_square_footage']
            )
            
            # Calculate actual expenses method
            actual_deduction = self._calculate_actual_home_office(
                home_office_data
            )
            
            return {
                'simplified_method': simplified_deduction,
                'actual_method': actual_deduction,
                'recommendation': self._recommend_home_office_method(
                    simplified_deduction,
                    actual_deduction
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing home office deduction: {str(e)}")
            raise

    def _calculate_standard_mileage(self, mileage_records: List[Dict[str, Any]]) -> Decimal:
        """Calculate standard mileage deduction"""
        total_miles = sum(record['distance'] for record in mileage_records)
        return Decimal(str(total_miles)) * self.deduction_categories['vehicle']['standard_rate']

    def _calculate_actual_vehicle_expenses(self, expenses: List[Dict[str, Any]]) -> Decimal:
        """Calculate actual vehicle expenses deduction"""
        return sum(Decimal(str(expense['amount'])) for expense in expenses)

    def _calculate_simplified_home_office(self, square_footage: int) -> Decimal:
        """Calculate simplified home office deduction"""
        max_footage = min(square_footage, 300)
        return Decimal(str(max_footage)) * Decimal('5')  # $5 per square foot

    def _calculate_actual_home_office(self, data: Dict[str, Any]) -> Decimal:
        """Calculate actual home office expenses"""
        total_home_expenses = sum(Decimal(str(amount)) for amount in data['home_expenses'].values())
        business_percentage = Decimal(str(data['office_square_footage'])) / \
                            Decimal(str(data['total_square_footage']))
        return total_home_expenses * business_percentage

    def _recommend_home_office_method(
        self,
        simplified: Decimal,
        actual: Decimal
    ) -> Dict[str, Any]:
        """Recommend best home office deduction method"""
        if simplified > actual:
            return {
                'method': 'simplified',
                'amount': simplified,
                'explanation': 'Simplified method provides higher deduction with less recordkeeping'
            }
        return {
            'method': 'actual',
            'amount': actual,
            'explanation': 'Actual expense method provides higher deduction'
        }

    def _generate_recommendations(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on opportunities"""
        recommendations = []
        
        # Group opportunities by category
        by_category = {}
        for opp in opportunities:
            category = opp['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(opp)
        
        # Generate category-specific recommendations
        for category, opps in by_category.items():
            total_potential = sum(op['deduction_potential'] for op in opps)
            recommendations.append({
                'category': category,
                'potential_amount': total_potential,
                'action_items': self._get_action_items(category, opps),
                'documentation_needed': self.deduction_categories[category]['documentation_required']
            })
        
        return recommendations

    def _get_action_items(self, category: str, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate specific action items for a category"""
        if category == 'vehicle':
            return [
                'Start tracking mileage for all business trips',
                'Keep receipts for all vehicle expenses',
                'Document business purpose for each trip'
            ]
        elif category == 'home_office':
            return [
                'Measure and document office space square footage',
                'Track all home-related expenses',
                'Take photos of home office setup'
            ]
        # Add more categories as needed
        return []
