from typing import Dict, Any, List
import logging
from datetime import datetime
from api.models.documents import Document, DocumentStatus
from api.services.audit.tax_audit_logger import TaxAuditLogger

class StatusTracker:
    """Service for tracking document status and verification workflow"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audit_logger = TaxAuditLogger()
        
        self.workflow_states = {
            'UPLOADED': {
                'next_states': ['PROCESSING', 'FAILED'],
                'required_checks': []
            },
            'PROCESSING': {
                'next_states': ['VALIDATED', 'FAILED'],
                'required_checks': ['virus_scan', 'format_check']
            },
            'VALIDATED': {
                'next_states': ['VERIFIED', 'REJECTED'],
                'required_checks': ['completeness', 'compliance']
            },
            'VERIFIED': {
                'next_states': ['ARCHIVED'],
                'required_checks': ['final_review']
            },
            'REJECTED': {
                'next_states': ['UPLOADED'],
                'required_checks': []
            },
            'FAILED': {
                'next_states': ['UPLOADED'],
                'required_checks': []
            },
            'ARCHIVED': {
                'next_states': [],
                'required_checks': []
            }
        }

    async def track_document_status(
        self,
        document_id: int,
        new_status: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Track document status changes"""
        try:
            document = await self._get_document(document_id)
            if not document:
                raise ValueError(f"Document not found: {document_id}")
                
            current_status = document.status
            
            # Validate status transition
            if not self._is_valid_transition(current_status, new_status):
                raise ValueError(f"Invalid status transition: {current_status} -> {new_status}")
                
            # Perform required checks
            check_results = await self._perform_required_checks(
                document, new_status
            )
            
            if not check_results['passed']:
                return {
                    'success': False,
                    'errors': check_results['errors']
                }
                
            # Update document status
            await self._update_document_status(
                document_id, new_status, metadata
            )
            
            # Log status change
            await self.audit_logger.log_status_change(
                document_id,
                current_status,
                new_status,
                metadata
            )
            
            return {
                'success': True,
                'previous_status': current_status,
                'new_status': new_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error tracking document status: {str(e)}")
            raise

    async def get_document_checklist(
        self,
        document_id: int
    ) -> Dict[str, Any]:
        """Get document verification checklist"""
        try:
            document = await self._get_document(document_id)
            if not document:
                raise ValueError(f"Document not found: {document_id}")
                
            current_state = document.status
            checklist = {
                'completed_checks': [],
                'pending_checks': [],
                'failed_checks': [],
                'current_state': current_state,
                'next_states': self.workflow_states[current_state]['next_states'],
                'required_checks': self.workflow_states[current_state]['required_checks']
            }
            
            # Get check history
            check_history = await self._get_check_history(document_id)
            
            for check in self.workflow_states[current_state]['required_checks']:
                if check in check_history:
                    if check_history[check]['passed']:
                        checklist['completed_checks'].append({
                            'check': check,
                            'timestamp': check_history[check]['timestamp'],
                            'metadata': check_history[check].get('metadata')
                        })
                    else:
                        checklist['failed_checks'].append({
                            'check': check,
                            'timestamp': check_history[check]['timestamp'],
                            'error': check_history[check].get('error')
                        })
                else:
                    checklist['pending_checks'].append(check)
            
            return checklist
            
        except Exception as e:
            self.logger.error(f"Error getting document checklist: {str(e)}")
            raise

    async def monitor_expiration(
        self,
        document_id: int
    ) -> Dict[str, Any]:
        """Monitor document expiration"""
        try:
            document = await self._get_document(document_id)
            if not document:
                raise ValueError(f"Document not found: {document_id}")
                
            expiration_info = {
                'has_expiration': False,
                'expiration_date': None,
                'days_until_expiration': None,
                'is_expired': False,
                'warnings': []
            }
            
            # Check document metadata for expiration
            metadata = document.metadata
            if 'expiration_date' in metadata:
                expiration_date = datetime.fromisoformat(metadata['expiration_date'])
                current_date = datetime.utcnow()
                
                days_until_expiration = (expiration_date - current_date).days
                
                expiration_info.update({
                    'has_expiration': True,
                    'expiration_date': metadata['expiration_date'],
                    'days_until_expiration': days_until_expiration,
                    'is_expired': days_until_expiration < 0
                })
                
                # Add warnings based on expiration
                if days_until_expiration < 0:
                    expiration_info['warnings'].append('Document has expired')
                elif days_until_expiration < 30:
                    expiration_info['warnings'].append('Document expires soon')
            
            return expiration_info
            
        except Exception as e:
            self.logger.error(f"Error monitoring expiration: {str(e)}")
            raise

    def _is_valid_transition(self, current_status: str, new_status: str) -> bool:
        """Check if status transition is valid"""
        if current_status not in self.workflow_states:
            return False
            
        return new_status in self.workflow_states[current_status]['next_states']

    async def _perform_required_checks(
        self,
        document: Document,
        new_status: str
    ) -> Dict[str, Any]:
        """Perform required checks for status transition"""
        try:
            required_checks = self.workflow_states[new_status]['required_checks']
            check_results = {
                'passed': True,
                'errors': []
            }
            
            for check in required_checks:
                result = await self._perform_check(document, check)
                if not result['passed']:
                    check_results['passed'] = False
                    check_results['errors'].append(result['error'])
            
            return check_results
            
        except Exception as e:
            self.logger.error(f"Error performing required checks: {str(e)}")
            raise

    async def _perform_check(
        self,
        document: Document,
        check: str
    ) -> Dict[str, Any]:
        """Perform individual check"""
        check_functions = {
            'virus_scan': self._check_virus_scan,
            'format_check': self._check_format,
            'completeness': self._check_completeness,
            'compliance': self._check_compliance,
            'final_review': self._check_final_review
        }
        
        if check not in check_functions:
            return {
                'passed': False,
                'error': f"Unknown check type: {check}"
            }
            
        return await check_functions[check](document)

    async def _check_virus_scan(self, document: Document) -> Dict[str, Any]:
        """Perform virus scan check"""
        # Implementation would integrate with virus scanning service
        return {'passed': True}

    async def _check_format(self, document: Document) -> Dict[str, Any]:
        """Perform format check"""
        # Implementation would check file format
        return {'passed': True}

    async def _check_completeness(self, document: Document) -> Dict[str, Any]:
        """Check document completeness"""
        # Implementation would check required fields
        return {'passed': True}

    async def _check_compliance(self, document: Document) -> Dict[str, Any]:
        """Check document compliance"""
        # Implementation would check compliance rules
        return {'passed': True}

    async def _check_final_review(self, document: Document) -> Dict[str, Any]:
        """Perform final review check"""
        # Implementation would check final review requirements
        return {'passed': True}

    async def _get_document(self, document_id: int) -> Document:
        """Get document by ID"""
        # Implementation would fetch document from database
        return None

    async def _update_document_status(
        self,
        document_id: int,
        new_status: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Update document status"""
        # Implementation would update document status in database
        pass

    async def _get_check_history(self, document_id: int) -> Dict[str, Any]:
        """Get document check history"""
        # Implementation would fetch check history from database
        return {}
