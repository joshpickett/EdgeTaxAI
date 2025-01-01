from typing import Dict, Any, List
import logging
from datetime import datetime

class DocumentRequirementConditions:
    """Service for handling conditional document requirements"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def evaluate_conditions(
        self,
        conditions: Dict[str, Any],
        user_answers: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate conditions and return required documents"""
        try:
            required_documents = []
            
            for condition_key, condition_data in conditions.items():
                trigger = condition_data.get('trigger')
                if self._evaluate_trigger(trigger, user_answers):
                    required_documents.extend(condition_data.get('required_docs', []))
            
            return required_documents
            
        except Exception as e:
            self.logger.error(f"Error evaluating conditions: {str(e)}")
            raise

    def _evaluate_trigger(self, trigger: str, answers: Dict[str, Any]) -> bool:
        """Evaluate trigger condition"""
        try:
            if not trigger:
                return False
                
            # Parse trigger condition
            field, operator, value = self._parse_trigger(trigger)
            
            # Get actual value from answers
            actual_value = answers.get(field)
            
            # Evaluate condition
            if operator == '==':
                return str(actual_value).lower() == str(value).lower()
            elif operator == '!=':
                return str(actual_value).lower() != str(value).lower()
            elif operator == '>':
                return float(actual_value) > float(value)
            elif operator == '<':
                return float(actual_value) < float(value)
                
            return False
            
        except Exception as e:
            self.logger.error(f"Error evaluating trigger: {str(e)}")
            return False

    def _parse_trigger(self, trigger: str) -> tuple:
        """Parse trigger string into components"""
        try:
            # Remove whitespace
            trigger = trigger.replace(' ', '')
            
            # Find operator
            operators = ['==', '!=', '>', '<']
            used_operator = None
            
            for operator in operators:
                if operator in trigger:
                    used_operator = operator
                    break
                    
            if not used_operator:
                raise ValueError(f"Invalid trigger format: {trigger}")
                
            # Split into field and value
            field, value = trigger.split(used_operator)
            
            # Clean up value
            value = value.strip('"\'')
            
            return field, used_operator, value
            
        except Exception as e:
            self.logger.error(f"Error parsing trigger: {str(e)}")
            raise

    def validate_conditions(self, conditions: Dict[str, Any]) -> List[str]:
        """Validate condition format"""
        errors = []
        
        for condition_key, condition_data in conditions.items():
            if not isinstance(condition_data, dict):
                errors.append(f"Invalid condition format for {condition_key}")
                continue
                
            if 'trigger' not in condition_data:
                errors.append(f"Missing trigger for condition {condition_key}")
                
            if 'required_docs' not in condition_data:
                errors.append(f"Missing required_docs for condition {condition_key}")
                
            if not isinstance(condition_data.get('required_docs', []), list):
                errors.append(f"Invalid required_docs format for {condition_key}")
                
        return errors
