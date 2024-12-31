from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.validation.real_time_validator import RealTimeValidator
from api.services.mef.validation_rules import ValidationRules
from api.utils.cache_utils import CacheManager

class FormValidationService:
    """Service for form validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = CacheManager()
        self.validation_rules = ValidationRules()
        self.real_time_validator = RealTimeValidator()
        self.cross_field_validators = self._initialize_cross_field_validators()

    @cache_response(timeout=3600)
    async def validate_section(
        self,
        form_type: str,
        section: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate form section"""
        try:
            cache_key = f"validation:{form_type}:{section}:{hash(str(data))}"
            cached_result = await self.cache.get(cache_key)
            
            if cached_result:
                return cached_result

            validation_result = await self.validator.validate_section(
                form_type, section, data
            )
            
            await self.cache.set(cache_key, validation_result, timeout=3600)
            return validation_result
            
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

    async def _validate_cross_fields(
        self,
        form_type: str,
        section: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate relationships between fields"""
        # Enhanced cross-field validation
        validators = self.cross_field_validators.get(form_type, {})
        section_validators = validators.get(section, [])
        
        results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_relationships': {}
        }

        return await self._apply_cross_field_validators(
            section_validators, data
        )
