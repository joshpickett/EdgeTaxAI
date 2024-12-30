from typing import Dict, Any, List
import logging
from decimal import Decimal
from datetime import datetime
from api.models.tax_forms import TaxForms
from api.services.mef.validation_rules import ValidationRules
from api.utils.tax_calculator import TaxCalculator

class TaxReviewService:
    """Service for comprehensive tax review and validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validator = ValidationRules()
        self.calculator = TaxCalculator()

    async def perform_comprehensive_review(
        self,
        user_id: int,
        tax_year: int
    ) -> Dict[str, Any]:
        """Perform comprehensive tax review"""
        try:
            # Get all tax forms and data
            forms = await self._get_user_tax_forms(user_id, tax_year)
            
            # Perform various checks
            calculations = await self._verify_calculations(forms)
            document_status = await self._check_required_documents(forms)
            schedule_review = await self._review_schedules(forms)
            deduction_review = await self._review_deductions(forms)
            
            return {
                'status': 'completed',
                'timestamp': datetime.utcnow().isoformat(),
                'calculations': calculations,
                'document_status': document_status,
                'schedule_review': schedule_review,
                'deduction_review': deduction_review,
                'recommendations': self._generate_recommendations(
                    calculations,
                    document_status,
                    schedule_review,
                    deduction_review
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error performing tax review: {str(e)}")
            raise

    async def _verify_calculations(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify all tax calculations"""
        try:
            total_income = Decimal('0')
            total_deductions = Decimal('0')
            total_credits = Decimal('0')
            
            for form in forms:
                if form['type'] == 'income':
                    total_income += Decimal(str(form['amount']))
                elif form['type'] == 'deduction':
                    total_deductions += Decimal(str(form['amount']))
                elif form['type'] == 'credit':
                    total_credits += Decimal(str(form['amount']))
            
            taxable_income = total_income - total_deductions
            calculated_tax = self.calculator.calculate_tax(taxable_income)
            final_tax = max(Decimal('0'), calculated_tax - total_credits)
            
            return {
                'total_income': str(total_income),
                'total_deductions': str(total_deductions),
                'total_credits': str(total_credits),
                'taxable_income': str(taxable_income),
                'calculated_tax': str(calculated_tax),
                'final_tax': str(final_tax)
            }
            
        except Exception as e:
            self.logger.error(f"Error verifying calculations: {str(e)}")
            raise

    async def _check_required_documents(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check status of required documents"""
        try:
            required_docs = set()
            submitted_docs = set()
            
            # Determine required documents based on forms
            for form in forms:
                required_docs.update(self._get_required_documents(form))
                if form.get('documents'):
                    submitted_docs.update(form['documents'])
            
            missing_docs = required_docs - submitted_docs
            
            return {
                'required': list(required_docs),
                'submitted': list(submitted_docs),
                'missing': list(missing_docs),
                'status': 'complete' if not missing_docs else 'incomplete'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking required documents: {str(e)}")
            raise

    async def _review_schedules(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review all schedules for completeness and accuracy"""
        try:
            schedule_status = {}
            
            for form in forms:
                if form.get('schedules'):
                    for schedule in form['schedules']:
                        schedule_status[schedule['type']] = {
                            'status': 'complete' if self._validate_schedule(schedule) else 'incomplete',
                            'missing_fields': self._get_missing_fields(schedule),
                            'warnings': self._get_schedule_warnings(schedule)
                        }
            
            return schedule_status
            
        except Exception as e:
            self.logger.error(f"Error reviewing schedules: {str(e)}")
            raise

    async def _review_deductions(self, forms: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review deductions for optimization opportunities"""
        try:
            deductions = []
            for form in forms:
                if form.get('deductions'):
                    for deduction in form['deductions']:
                        deductions.append({
                            'type': deduction['type'],
                            'amount': deduction['amount'],
                            'documentation': self._check_deduction_documentation(deduction),
                            'optimization_opportunities': self._find_optimization_opportunities(deduction)
                        })
            
            return {
                'deductions': deductions,
                'total_amount': sum(d['amount'] for d in deductions),
                'optimization_potential': self._calculate_optimization_potential(deductions)
            }
            
        except Exception as e:
            self.logger.error(f"Error reviewing deductions: {str(e)}")
            raise

    def _generate_recommendations(
        self,
        calculations: Dict[str, Any],
        document_status: Dict[str, Any],
        schedule_review: Dict[str, Any],
        deduction_review: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on review results"""
        recommendations = []
        
        # Check for missing documents
        if document_status['missing']:
            recommendations.append({
                'type': 'missing_documents',
                'priority': 'high',
                'message': 'Submit missing required documents',
                'items': document_status['missing']
            })
        
        # Check for schedule issues
        for schedule_type, status in schedule_review.items():
            if status['missing_fields']:
                recommendations.append({
                    'type': 'incomplete_schedule',
                    'priority': 'medium',
                    'message': f'Complete missing fields in {schedule_type}',
                    'items': status['missing_fields']
                })
        
        # Check for deduction opportunities
        if deduction_review.get('optimization_potential'):
            recommendations.append({
                'type': 'deduction_optimization',
                'priority': 'medium',
                'message': 'Consider additional deduction opportunities',
                'potential_savings': deduction_review['optimization_potential']
            })
        
        return recommendations

    # Helper methods for schedule validation
    def _validate_schedule(self, schedule: Dict[str, Any]) -> bool:
        """Validate individual schedule"""
        required_fields = self.validator.get_required_fields(schedule['type'])
        return all(field in schedule and schedule[field] for field in required_fields)

    def _get_missing_fields(self, schedule: Dict[str, Any]) -> List[str]:
        """Get list of missing required fields in schedule"""
        required_fields = self.validator.get_required_fields(schedule['type'])
        return [field for field in required_fields if not schedule.get(field)]

    def _get_schedule_warnings(self, schedule: Dict[str, Any]) -> List[str]:
        """Get warnings for schedule"""
        warnings = []
        warning_rules = self.validator.get_warning_rules(schedule['type'])
        
        for rule in warning_rules:
            if not self._check_warning_rule(schedule, rule):
                warnings.append(rule['message'])
                
        return warnings

    def _check_deduction_documentation(self, deduction: Dict[str, Any]) -> Dict[str, Any]:
        """Check documentation status for deduction"""
        required_docs = self.validator.get_required_documentation(deduction['type'])
        submitted_docs = deduction.get('documentation', [])
        
        return {
            'status': 'complete' if all(doc in submitted_docs for doc in required_docs) else 'incomplete',
            'missing': [doc for doc in required_docs if doc not in submitted_docs]
        }

    def _find_optimization_opportunities(self, deduction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential optimization opportunities for deduction"""
        opportunities = []
        rules = self.validator.get_optimization_rules(deduction['type'])
        
        for rule in rules:
            if self._check_optimization_rule(deduction, rule):
                opportunities.append({
                    'type': rule['type'],
                    'description': rule['description'],
                    'potential_savings': rule['potential_savings']
                })
                
        return opportunities

    def _calculate_optimization_potential(self, deductions: List[Dict[str, Any]]) -> Decimal:
        """Calculate total optimization potential"""
        return sum(
            Decimal(str(opportunity['potential_savings']))
            for deduction in deductions
            for opportunity in deduction['optimization_opportunities']
        )
