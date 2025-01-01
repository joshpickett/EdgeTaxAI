from typing import Dict, Any, List
import logging
from api.services.validation.validation_rules import ValidationRules
from api.services.validation.validation_manager import ValidationManager
from api.services.validation.category_manager import CategoryManager
from api.utils.cache_utils import CacheManager

class FormValidationService:
    """Service for form validation"""
    
    def __init__(self):
        self.validator = ValidationRules()
        self.validation_manager = ValidationManager()
        self.category_manager = CategoryManager()
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()

    async def validate_section(
        self,
        form_type: str,
        section: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate form section"""
        try:
            validation_result = await self.validator.validate_section(form_type, section, data)
            
            # Add enhanced validation using ValidationManager
            categories = self._get_section_categories(form_type, section)
            for category in categories:
                category_validation = await self.validation_manager.validate_document(
                    data, category
                )
                validation_result = self._merge_validation_results(
                    validation_result, 
                    category_validation
                )
            
            # Add cross-category validation
            cross_validation = await self._validate_cross_categories(data, categories)
            return self._merge_validation_results(validation_result, cross_validation)
             
        except Exception as e:
            self.logger.error(f"Error validating section: {str(e)}")
            raise

    async def validate_field(
        self,
        form_type: str,
        field_name: str,
        value: Any,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Validate individual field"""
        try:
            return await self.validator.validate_field(
                form_type, field_name, value, context
            )
        except Exception as e:
            self.logger.error(f"Error validating field: {str(e)}")
            raise

    async def validate_dependencies(
        self,
        form_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate form field dependencies"""
        try:
            dependencies = self.validation_rules.get_dependencies(form_type)
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            for dependency in dependencies:
                field = dependency['field']
                dependent_field = dependency['depends_on']
                
                if dependent_field in data and field not in data:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append({
                        'field': field,
                        'type': 'dependency',
                        'message': f'Required when {dependent_field} is provided'
                    })
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating dependencies: {str(e)}")
            raise

    async def validate_form_completeness(
        self,
        form_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate overall form completeness"""
        try:
            validation_result = await self.validation_rules.validate_form_completeness(
                form_type, data
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating form completeness: {str(e)}")
            raise

    async def validate_schedule_e(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Schedule E data"""
        errors = []
        warnings = []

        # Validate properties
        for index, property_data in enumerate(data.get('properties', [])):
            if not property_data.get('address'):
                errors.append({
                    'field': f'property_{index}_address',
                    'message': f'Address is required for property {index + 1}'
                })

            # Validate rental days
            total_days = property_data.get('daysRented', 0) + property_data.get('personalUse', 0)
            if total_days > 365:
                errors.append({
                    'field': f'property_{index}_days',
                    'message': f'Total days for property {index + 1} cannot exceed 365'
                })

        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _generate_field_suggestions(
        self,
        errors: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate field-specific suggestions"""
        suggestions = []
        
        for error in errors:
            field = error['field']
            error_type = error['type']
            
            suggestion = {
                'field': field,
                'suggestion': self._get_suggestion(error_type)
            }
            
            suggestions.append(suggestion)
            
        return suggestions

    def _get_suggestion(self, error_type: str) -> str:
        """Get suggestion based on error type"""
        suggestion_map = {
            'required': 'This field is required for IRS compliance',
            'format': 'Please check the format and try again',
            'range': 'The value entered is outside acceptable range',
            'dependency': 'This field is required based on other information provided',
            'calculation': 'Please verify your calculations'
        }
        return suggestion_map.get(error_type, 'Please verify this field')

    async def _validate_cross_categories(
        self,
        data: Dict[str, Any],
        categories: List[str]
    ) -> Dict[str, Any]:
        """Validate relationships between categories"""
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }

            # Get cross-category rules
            rules = self.category_manager.get_cross_category_rules(categories)
            
            # Apply each rule
            for rule in rules:
                rule_result = await self._apply_cross_category_rule(data, rule)
                if not rule_result['is_valid']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].extend(rule_result['errors'])
                validation_result['warnings'].extend(rule_result['warnings'])

            return validation_result

        except Exception as e:
            self.logger.error(f"Error in cross-category validation: {str(e)}")
            raise

    async def _apply_cross_category_rule(
        self,
        data: Dict[str, Any],
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply individual cross-category validation rule"""
        try:
            rule_type = rule.get('type')
            if rule_type == 'dependency':
                return self._validate_category_dependency(data, rule)
            elif rule_type == 'exclusion':
                return self._validate_category_exclusion(data, rule)
            elif rule_type == 'requirement':
                return self._validate_category_requirement(data, rule)
            
            return {'is_valid': True, 'errors': [], 'warnings': []}
            
        except Exception as e:
            self.logger.error(f"Error applying cross-category rule: {str(e)}")
            raise

    def _validate_category_dependency(
        self,
        data: Dict[str, Any],
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate category dependency rule"""
        try:
            dependent_category = rule.get('dependent_category')
            required_category = rule.get('required_category')
            
            if self._has_category_data(data, dependent_category) and \
               not self._has_category_data(data, required_category):
                return {
                    'is_valid': False,
                    'errors': [{
                        'type': 'category_dependency',
                        'message': f'{required_category} is required when {dependent_category} is present'
                    }],
                    'warnings': []
                }
            
            return {'is_valid': True, 'errors': [], 'warnings': []}
            
        except Exception as e:
            self.logger.error(f"Error validating category dependency: {str(e)}")
            raise

    def _has_category_data(self, data: Dict[str, Any], category: str) -> bool:
        """Check if data contains information for a category"""
        category_fields = self.category_manager.get_category_fields(category)
        return any(field in data for field in category_fields)
