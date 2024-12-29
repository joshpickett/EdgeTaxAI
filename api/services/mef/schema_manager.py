from typing import Dict, Any, Optional
import os
import json
import logging
from lxml import etree
from datetime import datetime
from api.config.mef_config import MEF_CONFIG

class SchemaManager:
    """Manage XML schemas for IRS submissions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.schema_path = MEF_CONFIG['VALIDATION']['SCHEMA_PATH']
        self.schema_versions = MEF_CONFIG['VALIDATION']['SCHEMA_VERSIONS']
        self.schema_cache = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all available schemas into memory"""
        try:
            for form_type, version in self.schema_versions.items():
                schema_file = f"{self.schema_path}/{form_type.lower()}_{version}.xsd"
                with open(schema_file, 'rb') as f:
                    self.schema_cache[form_type] = {
                        'schema': etree.XMLSchema(etree.parse(f)),
                        'version': version,
                        'loaded_at': datetime.utcnow()
                    }
        except Exception as e:
            self.logger.error(f"Error loading schemas: {str(e)}")
            raise

    def detect_version(self, xml_content: str) -> Dict[str, Any]:
        """Detect schema version from XML content"""
        try:
            root = etree.fromstring(xml_content.encode())
            namespace = root.nsmap.get(None)
            
            # Extract version from namespace or root attributes
            version = root.get('version') or self._extract_version_from_namespace(namespace)
            
            return {
                'version': version,
                'namespace': namespace,
                'form_type': self._detect_form_type(root)
            }
        except Exception as e:
            self.logger.error(f"Error detecting schema version: {str(e)}")
            raise

    def validate_schema(self, 
                       xml_content: str, 
                       form_type: str,
                       version: Optional[str] = None) -> Dict[str, Any]:
        """Validate XML against schema"""
        try:
            if version and version != self.schema_versions[form_type]:
                return self._validate_with_backward_compatibility(
                    xml_content, form_type, version
                )
            
            schema = self.schema_cache[form_type]['schema']
            xml_doc = etree.fromstring(xml_content.encode())
            
            try:
                schema.assertValid(xml_doc)
                return {'is_valid': True, 'errors': None}
            except etree.DocumentInvalid as e:
                return {
                    'is_valid': False,
                    'errors': self._format_validation_errors(e)
                }
                
        except Exception as e:
            self.logger.error(f"Error validating schema: {str(e)}")
            raise

    def _validate_with_backward_compatibility(self,
                                           xml_content: str,
                                           form_type: str,
                                           version: str) -> Dict[str, Any]:
        """Validate XML with backward compatibility"""
        try:
            # Load historical schema version
            historical_schema_file = f"{self.schema_path}/{form_type.lower()}_{version}.xsd"
            with open(historical_schema_file, 'rb') as f:
                historical_schema = etree.XMLSchema(etree.parse(f))
            
            xml_doc = etree.fromstring(xml_content.encode())
            
            try:
                historical_schema.assertValid(xml_doc)
                return {'is_valid': True, 'errors': None}
            except etree.DocumentInvalid as e:
                return {
                    'is_valid': False,
                    'errors': self._format_validation_errors(e)
                }
                
        except Exception as e:
            self.logger.error(f"Error validating with backward compatibility: {str(e)}")
            raise

    def _detect_form_type(self, root: etree.Element) -> str:
        """Detect form type from XML structure"""
        form_indicators = {
            '1099NEC': ['NonemployeeComp', 'Form1099NEC'],
            '1099K': ['PaymentCard', 'Form1099K'],
            '1040': ['Form1040', 'IndividualIncomeTax'],
            'SCHEDULE_C': ['ScheduleC', 'BusinessIncome']
        }
        
        for form_type, indicators in form_indicators.items():
            if any(root.find(f'.//{indicator}') is not None for indicator in indicators):
                return form_type
                
        return 'UNKNOWN'

    def _extract_version_from_namespace(self, namespace: str) -> Optional[str]:
        """Extract version from namespace URI"""
        if namespace and 'version' in namespace:
            return namespace.split('version=')[-1].split('&')[0]
        return None

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
