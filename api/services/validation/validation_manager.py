from typing import Dict, Any, List
import logging
from datetime import datetime
from api.services.category.category_manager import CategoryManager
from api.services.error_handling_service import ErrorHandlingService

class ValidationManager:
    """Service for managing document validation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.performance_logger = PerformanceLogger()
        self.category_manager = CategoryManager()
        self.error_service = ErrorHandlingService()
        
        # Define quality scoring weights
        self.quality_weights = {
            'completeness': 0.4,
            'clarity': 0.3,
            'compliance': 0.3
        }

    async def validate_document(
        self,
        document: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Validate document and calculate quality score"""
        try:
            start_time = datetime.utcnow()
            # Validate against category rules
            category_validation = self.category_manager.validate_category(
                category, document
            )
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(document, category)
            
            # Check cross-category validation rules
            cross_validation = await self._validate_cross_category(
                document, category
            )
            
            # Log performance metrics
            await self.performance_logger.log_metrics({
                'operation': 'validate_document',
                'duration': (datetime.utcnow() - start_time).total_seconds(),
                'category': category
            })
            
            validation_result = {
                'is_valid': category_validation['is_valid'] and cross_validation['is_valid'],
                'quality_score': quality_score,
                'errors': [
                    *category_validation.get('errors', []),
                    *cross_validation.get('errors', [])
                ],
                'warnings': [
                    *category_validation.get('warnings', []),
                    *cross_validation.get('warnings', [])
                ],
                'deadline_status': await self._check_deadlines(document, category)
            }
            
            # Handle validation errors if any
            if not validation_result['is_valid']:
                await self.error_service.handle_error(
                    Exception("Validation failed"),
                    {
                        'document_id': document.get('id'),
                        'category': category,
                        'errors': validation_result['errors']
                    },
                    'VALIDATION'
                )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating document: {str(e)}")
            raise

    def _calculate_quality_score(
        self,
        document: Dict[str, Any],
        category: str
    ) -> float:
        """Calculate document quality score"""
        try:
            scores = {
                'completeness': self._calculate_completeness(document, category),
                'clarity': self._calculate_clarity(document),
                'compliance': self._calculate_compliance(document, category)
            }
            
            weighted_score = sum(
                scores[metric] * self.quality_weights[metric]
                for metric in scores
            )
            
            return round(weighted_score, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating quality score: {str(e)}")
            return 0.0

    async def _validate_cross_category(
        self,
        document: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Validate cross-category rules"""
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Get related categories
            related_categories = self.category_manager.get_related_categories(category)
            
            # Check cross-category rules
            for related_category in related_categories:
                related_validation = await self._check_related_category(
                    document, category, related_category
                )
                
                if not related_validation['is_valid']:
                    validation_result['is_valid'] = False
                    validation_result['errors'].extend(related_validation['errors'])
                    validation_result['warnings'].extend(related_validation['warnings'])
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating cross-category rules: {str(e)}")
            raise

    def _check_deadlines(
        self,
        document: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Check document deadlines"""
        try:
            metadata = self.category_manager.get_category_metadata(category)
            deadlines = metadata.get('deadlines', {})
            
            current_date = datetime.utcnow()
            deadline_status = {
                'has_deadlines': bool(deadlines),
                'upcoming_deadlines': [],
                'overdue_deadlines': []
            }
            
            for deadline_type, deadline_date in deadlines.items():
                deadline = datetime.fromisoformat(deadline_date)
                if deadline < current_date:
                    deadline_status['overdue_deadlines'].append({
                        'type': deadline_type,
                        'deadline': deadline_date
                    })
                else:
                    deadline_status['upcoming_deadlines'].append({
                        'type': deadline_type,
                        'deadline': deadline_date
                    })
            
            return deadline_status
            
        except Exception as e:
            self.logger.error(f"Error checking deadlines: {str(e)}")
            return {'has_deadlines': False}

    def _calculate_completeness(
        self,
        document: Dict[str, Any],
        category: str
    ) -> float:
        """Calculate document completeness score"""
        try:
            required_fields = self.category_manager.get_category_rules(category).get('required_fields', [])
            if not required_fields:
                return 1.0
                
            present_fields = sum(1 for field in required_fields if field in document)
            return present_fields / len(required_fields)
            
        except Exception as e:
            self.logger.error(f"Error calculating completeness: {str(e)}")
            return 0.0

    def _calculate_clarity(self, document: Dict[str, Any]) -> float:
        """Calculate document clarity score"""
        # Implementation would include image quality checks, OCR confidence scores, etc.
        return 1.0

    def _calculate_compliance(
        self,
        document: Dict[str, Any],
        category: str
    ) -> float:
        """Calculate compliance score"""
        try:
            rules = self.category_manager.get_category_rules(category)
            total_rules = len(rules)
            if not total_rules:
                return 1.0
                
            passed_rules = sum(1 for rule in rules if self._check_rule(document, rule))
            return passed_rules / total_rules
            
        except Exception as e:
            self.logger.error(f"Error calculating compliance: {str(e)}")
            return 0.0

    def _check_rule(self, document: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if document passes a specific rule"""
        rule_type = rule.get('type')
        if rule_type == 'required_fields':
            return all(field in document for field in rule['fields'])
        elif rule_type == 'format_checks':
            return all(self._check_format(document, format_check) for format_check in rule['formats'])
        return True

    async def _check_related_category(
        self,
        document: Dict[str, Any],
        category: str,
        related_category: str
    ) -> Dict[str, Any]:
        """Check validation rules between related categories"""
        # Implementation would check relationships between categories
        return {'is_valid': True, 'errors': [], 'warnings': []}