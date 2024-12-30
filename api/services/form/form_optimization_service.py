from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.credit_optimization_service import CreditOptimizationService
from api.services.deduction_optimization_service import DeductionOptimizationService
from api.services.schedule_optimizer import ScheduleOptimizer

class FormOptimizationService:
    """Service for optimizing form completion"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.credit_optimizer = CreditOptimizationService()
        self.deduction_optimizer = DeductionOptimizationService()
        self.schedule_optimizer = ScheduleOptimizer()

    async def analyze_optimization_opportunities(
        self,
        user_id: int,
        form_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze form for optimization opportunities"""
        try:
            # Add enhanced optimization analysis
            deduction_opportunities = await self.deduction_optimizer.analyze_deduction_opportunities(
                user_id, data.get('tax_year')
            )
            
            schedule_opportunities = await self.schedule_optimizer.optimize(
                data.get('schedules', [])
            )
            
            # Calculate credit opportunities
            credit_opportunities = await self.credit_optimizer.analyze_credit_opportunities(
                user_id, data.get('tax_year')
            )
            
            return {
                'credit_opportunities': credit_opportunities,
                'deduction_opportunities': deduction_opportunities,
                'schedule_opportunities': schedule_opportunities,
                'total_potential_savings': self._calculate_total_savings(
                    credit_opportunities,
                    deduction_opportunities
                ),
                'recommendations': self._generate_recommendations(
                    credit_opportunities,
                    deduction_opportunities,
                    schedule_opportunities
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing optimization opportunities: {str(e)}")
            raise

    def _calculate_total_savings(
        self,
        credit_opportunities: Dict[str, Any],
        deduction_opportunities: Dict[str, Any]
    ) -> float:
        """Calculate total potential savings"""
        credit_savings = credit_opportunities.get('total_potential', 0)
        deduction_savings = deduction_opportunities.get('total_potential', 0)
        return credit_savings + deduction_savings

    def _generate_recommendations(
        self,
        credit_opportunities: Dict[str, Any],
        deduction_opportunities: Dict[str, Any],
        schedule_opportunities: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate specific recommendations"""
        # Enhanced recommendation generation
        recommendations = []
        
        for opportunity in credit_opportunities.get('opportunities', []) + \
                          deduction_opportunities.get('opportunities', []) + \
                          schedule_opportunities.get('opportunities', []):
            recommendations.append({
                'type': opportunity['type'],
                'description': opportunity['description'],
                'potential_savings': opportunity['potential_savings'],
                'priority': self._calculate_priority(opportunity['potential_savings']),
                'implementation_difficulty': opportunity['difficulty']
            })
        
        return sorted(
            recommendations,
            key=lambda x: x['potential_savings'],
            reverse=True
        )

    def _calculate_priority(self, amount: float) -> str:
        """Calculate recommendation priority based on amount"""
        if amount >= 1000:
            return 'high'
        elif amount >= 500:
            return 'medium'
        return 'low'

    def _prioritize_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize opportunities based on potential savings"""
        for opportunity in opportunities:
            opportunity['priority'] = self._calculate_priority(opportunity['potential_savings'])
        return opportunities
