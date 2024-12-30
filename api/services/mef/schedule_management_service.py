from typing import Dict, Any, List
import logging
from api.models.tax_forms import TaxForms, FormType
from api.services.mef.schedule_attachment_manager import ScheduleAttachmentManager
from api.services.mef.validation_rules import ValidationRules
from api.services.mef.cross_schedule_calculator import CrossScheduleCalculator
from api.services.mef.schedule_optimizer import ScheduleOptimizer

class ScheduleManagementService:
    """Manage tax schedules and their dependencies"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.attachment_manager = ScheduleAttachmentManager()
        self.validator = ValidationRules()
        self.schedule_optimizer = ScheduleOptimizer()
        
        # Define schedule dependencies
        self.schedule_dependencies = {
            'SCHEDULE_C': {
                'required_forms': ['1040'],
                'triggers': ['business_income', 'self_employment'],
                'required_fields': ['business_name', 'ein', 'business_address']
            },
            'SCHEDULE_SE': {
                'required_forms': ['1040', 'SCHEDULE_C'],
                'triggers': ['self_employment_income'],
                'threshold': 400  # $400 SE income threshold
            },
            'SCHEDULE_E': {
                'required_forms': ['1040'],
                'triggers': ['rental_income', 'partnership_income'],
                'required_fields': ['property_address', 'rental_income']
            }
        }

    async def determine_required_schedules(self, tax_data: Dict[str, Any]) -> List[str]:
        """Determine which schedules are required based on tax data"""
        try:
            required_schedules = []
            
            # Check Schedule C requirement
            if self._needs_schedule_c(tax_data):
                required_schedules.append('SCHEDULE_C')
                
            # Check Schedule SE requirement
            if self._needs_schedule_se(tax_data):
                required_schedules.append('SCHEDULE_SE')
                
            # Check Schedule E requirement
            if self._needs_schedule_e(tax_data):
                required_schedules.append('SCHEDULE_E')
                
            return required_schedules
            
        except Exception as e:
            self.logger.error(f"Error determining required schedules: {str(e)}")
            raise

    def validate_schedule_dependencies(self, schedules: List[str]) -> Dict[str, Any]:
        """Validate schedule dependencies"""
        try:
            validation_results = {
                'is_valid': True,
                'missing_dependencies': [],
                'invalid_combinations': []
            }
            
            for schedule in schedules:
                deps = self.schedule_dependencies.get(schedule, {})
                
                # Check required forms
                for required_form in deps.get('required_forms', []):
                    if required_form not in schedules:
                        validation_results['missing_dependencies'].append({
                            'schedule': schedule,
                            'missing': required_form
                        })
                        validation_results['is_valid'] = False
                        
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating schedule dependencies: {str(e)}")
            raise

    async def calculate_cross_schedule_totals(self, schedules: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate totals across multiple schedules"""
        try:
            return await self.cross_calculator.calculate_totals(schedules)
        except Exception as e:
            self.logger.error(f"Error calculating cross-schedule totals: {str(e)}")
            raise

    async def validate_cross_schedule_consistency(self, schedules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency between related schedules"""
        try:
            validation_results = await self.cross_calculator.validate_consistency(schedules)
            return validation_results
        except Exception as e:
            self.logger.error(f"Error validating cross-schedule consistency: {str(e)}")
            raise

    def _needs_schedule_c(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Schedule C is needed"""
        income_sources = tax_data.get('income_sources', {})
        return (
            income_sources.get('business_income', 0) > 0 or
            income_sources.get('self_employment', 0) > 0
        )

    def _needs_schedule_se(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Schedule SE is needed"""
        self_employment_income = tax_data.get('income_sources', {}).get('self_employment_income', 0)
        return self_employment_income > self.schedule_dependencies['SCHEDULE_SE']['threshold']

    def _needs_schedule_e(self, tax_data: Dict[str, Any]) -> bool:
        """Determine if Schedule E is needed"""
        income_sources = tax_data.get('income_sources', {})
        return (
            income_sources.get('rental_income', 0) > 0 or
            income_sources.get('partnership_income', 0) > 0
        )

    async def generate_schedule(self, schedule_type: str, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schedule data structure"""
        try:
            # Validate schedule requirements
            if not self._validate_schedule_requirements(schedule_type, tax_data):
                raise ValueError(f"Missing required data for {schedule_type}")
                
            # Generate schedule-specific data
            schedule_data = await self._generate_schedule_data(schedule_type, tax_data)
            
            # Validate generated data
            validation_result = self.validator.validate_schedule(schedule_type, schedule_data)
            if not validation_result['is_valid']:
                raise ValueError(f"Invalid schedule data: {validation_result['errors']}")
                
            return schedule_data
            
        except Exception as e:
            self.logger.error(f"Error generating schedule: {str(e)}")
            raise

    def _validate_schedule_requirements(self, schedule_type: str, tax_data: Dict[str, Any]) -> bool:
        """Validate that all required fields are present"""
        required_fields = self.schedule_dependencies.get(schedule_type, {}).get('required_fields', [])
        
        for field in required_fields:
            if not self._get_nested_value(tax_data, field):
                return False
                
        return True

    def _get_nested_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get nested dictionary value using dot notation"""
        parts = field.split('.')
        value = data
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
                
        return value

    async def _generate_schedule_data(self, schedule_type: str, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schedule-specific data structure"""
        generators = {
            'SCHEDULE_C': self._generate_schedule_c,
            'SCHEDULE_SE': self._generate_schedule_se,
            'SCHEDULE_E': self._generate_schedule_e
        }
        
        generator = generators.get(schedule_type)
        if not generator:
            raise ValueError(f"Unsupported schedule type: {schedule_type}")
            
        return await generator(tax_data)

    async def _generate_schedule_c(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schedule C data"""
        business_data = tax_data.get('business', {})
        
        return {
            'business_name': business_data.get('name'),
            'ein': business_data.get('ein'),
            'business_address': business_data.get('address'),
            'accounting_method': business_data.get('accounting_method', 'Cash'),
            'income': {
                'gross_receipts': business_data.get('gross_receipts', 0),
                'returns': business_data.get('returns', 0),
                'other_income': business_data.get('other_income', 0)
            },
            'expenses': business_data.get('expenses', {})
        }

    async def _generate_schedule_se(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schedule SE data"""
        self_employment_income = tax_data.get('income_sources', {}).get('self_employment_income', 0)
        
        return {
            'self_employment_income': self_employment_income,
            'church_income': tax_data.get('church_income', 0),
            'farm_income': tax_data.get('farm_income', 0)
        }

    async def _generate_schedule_e(self, tax_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Schedule E data"""
        rental_properties = tax_data.get('rental_properties', [])
        
        return {
            'properties': [
                {
                    'address': prop.get('address'),
                    'type': prop.get('type'),
                    'income': prop.get('income', {}),
                    'expenses': prop.get('expenses', {})
                }
                for prop in rental_properties
            ]
        }

    async def optimize_schedule_order(self, schedules: List[str]) -> List[str]:
        """Optimize the order of schedule processing"""
        try:
            return await self.schedule_optimizer.optimize(schedules)
        except Exception as e:
            self.logger.error(f"Error optimizing schedule order: {str(e)}")
            raise

    async def validate_schedule_completeness(self, schedule_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate schedule completeness"""
        try:
            validation_result = await self.validator.validate_completeness(
                schedule_type, data
            )
            return validation_result
        except Exception as e:
            self.logger.error(f"Error validating schedule completeness: {str(e)}")
            raise
