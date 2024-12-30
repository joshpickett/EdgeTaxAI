from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.validation.real_time_validator import RealTimeValidator
from api.services.mef.validation_rules import ValidationRules

class FormValidationService:
    """Service for form validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_rules = ValidationRules()
        self.validator = RealTimeValidator()

    async def validate_section(
        self,
        form_type: str,
        section: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate form section"""
        try:
            # Perform real-time validation
            validation_result = await self.validator.validate_section(
                form_type, section, data
            )
            
            # Add field-specific suggestions
            validation_result['suggestions'] = self._generate_field_suggestions(
                validation_result['errors']
            )
            
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
        suggestions = {
            'required': 'This field is required for IRS compliance',
            'format': 'Please check the format and try again',
            'range': 'The value entered is outside acceptable range',
            'dependency': 'This field is required based on other information provided',
            'calculation': 'Please verify your calculations'
        }
        return suggestions.get(error_type, 'Please verify this field')
