from typing import Dict, Any, Optional
import logging
from lxml import etree
import os
from api.config.mef_config import MEF_CONFIG

class MeFValidator:
    def __init__(self):
        self.schema_path = MEF_CONFIG['VALIDATION']['SCHEMA_PATH']
        self.schemas = self._load_schemas()
        self.logger = logging.getLogger(__name__)

    def _load_schemas(self) -> Dict[str, etree.XMLSchema]:
        """Load all IRS XML schemas"""
        schemas = {}
        try:
            for form_type, version in MEF_CONFIG['VALIDATION']['SCHEMA_VERSIONS'].items():
                schema_file = f"{self.schema_path}/{form_type.lower()}_{version}.xsd"
                with open(schema_file, 'rb') as f:
                    schema_document = etree.parse(f)
                    schemas[form_type] = etree.XMLSchema(schema_document)
            return schemas
        except Exception as e:
            self.logger.error(f"Error loading schemas: {str(e)}")
            raise

    def validate_xml(self, xml_string: str, form_type: str) -> Dict[str, Any]:
        """Validate XML against IRS schema"""
        try:
            # Parse XML
            xml_document = etree.fromstring(xml_string.encode())
            
            # Get appropriate schema
            schema = self.schemas.get(form_type)
            if not schema:
                raise ValueError(f"No schema found for form type: {form_type}")
            
            # Validate
            schema.assertValid(xml_document)
            
            return {
                'is_valid': True,
                'errors': None
            }
            
        except etree.DocumentInvalid as e:
            self.logger.error(f"XML validation error: {str(e)}")
            return {
                'is_valid': False,
                'errors': self._format_validation_errors(e)
            }
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise

    def _format_validation_errors(self, error: etree.DocumentInvalid) -> list:
        """Format validation errors into readable messages"""
        return [
            {
                'line': err.line,
                'column': err.column,
                'message': err.message,
                'path': err.path
            }
            for err in error.error_log
        ]

    def validate_business_rules(self, xml_document: etree.Element, form_type: str) -> Dict[str, Any]:
        """Validate business rules specific to form type"""
        try:
            rules = self._get_business_rules(form_type)
            violations = []
            
            for rule in rules:
                if not self._check_rule(xml_document, rule):
                    violations.append(rule['message'])
            
            return {
                'is_valid': len(violations) == 0,
                'violations': violations
            }
            
        except Exception as e:
            self.logger.error(f"Business rule validation error: {str(e)}")
            raise

    def _get_business_rules(self, form_type: str) -> list:
        """Get business rules for specific form type"""
        rules = {
            '1099K': [
                {
                    'xpath': '//GrossAmount',
                    'rule': lambda x: float(x) >= 0,
                    'message': 'Gross amount cannot be negative'
                },
                {
                    'xpath': '//CardTransactions',
                    'rule': lambda x: int(x) >= 0,
                    'message': 'Number of transactions cannot be negative'
                }
            ]
        }
        return rules.get(form_type, [])
