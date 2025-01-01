from typing import Dict, Any, List
import logging
from datetime import datetime
import yaml
import os
from api.config.document_requirements.2023.categories import categories_config

class CategoryManager:
    """Service for managing document categories and inheritance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.categories = self._load_categories()
        self.validation_rules = {}
        self.relationships = {}

    def _load_categories(self) -> Dict[str, Any]:
        """Load category configuration"""
        try:
            with open(categories_config, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Error loading categories: {str(e)}")
            raise

    def get_category_rules(self, category: str) -> Dict[str, Any]:
        """Get validation rules for category"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
            
        rules = self.categories[category].get('validation_rules', {})
        
        # Check for inherited rules
        parent = self.categories[category].get('inherits_from')
        if parent:
            parent_rules = self.get_category_rules(parent)
            rules = self._merge_rules(parent_rules, rules)
            
        return rules

    def validate_category(self, category: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """Validate document against category rules"""
        try:
            rules = self.get_category_rules(category)
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Validate required fields
            for field in rules.get('required_fields', []):
                if field not in document:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Missing required field: {field}")
            
            # Validate format checks
            for format_check in rules.get('format_checks', []):
                if not self._check_format(document, format_check):
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"Invalid format: {format_check}")
            
            # Validate file size
            max_size = rules.get('max_size')
            if max_size and document.get('size', 0) > max_size:
                validation_result['is_valid'] = False
                validation_result['errors'].append("File size exceeds maximum allowed")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating category: {str(e)}")
            raise

    def get_category_metadata(self, category: str) -> Dict[str, Any]:
        """Get metadata requirements for category"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
            
        metadata = self.categories[category].get('metadata', {})
        
        # Check for inherited metadata
        parent = self.categories[category].get('inherits_from')
        if parent:
            parent_metadata = self.get_category_metadata(parent)
            metadata = self._merge_metadata(parent_metadata, metadata)
            
        return metadata

    def get_related_categories(self, category: str) -> List[str]:
        """Get related categories"""
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
            
        relationships = self.categories[category].get('relationships', {})
        return relationships.get('related', [])

    def _merge_rules(self, parent_rules: Dict[str, Any], child_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Merge parent and child validation rules"""
        merged = parent_rules.copy()
        
        for key, value in child_rules.items():
            if key in merged and isinstance(merged[key], list):
                merged[key].extend(value)
            else:
                merged[key] = value
                
        return merged

    def _merge_metadata(self, parent_metadata: Dict[str, Any], child_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Merge parent and child metadata requirements"""
        merged = parent_metadata.copy()
        
        for key, value in child_metadata.items():
            if key in merged and isinstance(merged[key], dict):
                merged[key].update(value)
            else:
                merged[key] = value
                
        return merged

    def _check_format(self, document: Dict[str, Any], format_check: str) -> bool:
        """Check document format"""
        if format_check == 'pdf':
            return document.get('mime_type') == 'application/pdf'
        elif format_check in ['jpg', 'png']:
            return document.get('mime_type', '').startswith('image/')
        return True
