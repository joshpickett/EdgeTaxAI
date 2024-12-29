from typing import Dict, Any, Optional
from datetime import datetime
import logging
from xml.etree import ElementTree
from api.config.mef_config import MEF_CONFIG
from api.services.mef.templates.form_1099nec import Form1099NECTemplate
from api.services.mef.templates.form_1099k import Form1099KTemplate
from api.services.mef.validation_rules import ValidationRules
from api.utils.mef_validator import MeFValidator
from api.models.mef_submissions import MeFSubmission, SubmissionStatus
from api.utils.retry_handler import with_retry
from decimal import Decimal
from api.services.mef.schedule_attachment_manager import ScheduleAttachmentManager
from .mef.xml_signer import XMLSigner
from .mef.pki_manager import PKIManager
from .mef.xml_optimizer import XMLOptimizer
from .mef.schema_manager import SchemaManager

class AcknowledgmentProcessor:
    """Process IRS acknowledgments"""
    
    @staticmethod
    def process_acknowledgment(ack_xml: str) -> Dict[str, Any]:
        """Process acknowledgment XML from IRS"""
        try:
            root = ElementTree.fromstring(ack_xml)
            return {
                'status': root.find('.//Status').text,
                'timestamp': root.find('.//Timestamp').text,
                'submission_id': root.find('.//SubmissionId').text,
                'errors': [
                    {'code': err.find('Code').text, 'message': err.find('Message').text}
                    for err in root.findall('.//Error')
                ]
            }
        except Exception as e:
            raise ValueError(f"Invalid acknowledgment XML: {str(e)}")

class MeFService:
    def __init__(self):
        self.validator = MeFValidator()
        self.xml_optimizer = XMLOptimizer()
        self.schema_manager = SchemaManager()
        self.xml_signer = XMLSigner()
        self.schedule_manager = ScheduleAttachmentManager()
        self.logger = logging.getLogger(__name__)

    @with_retry(max_attempts=3, initial_delay=1.0)
    async def _submit_to_irs(self, xml_content: str, form_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit XML to IRS"""
        try:
            # Validate file size
            if len(xml_content.encode()) > MEF_CONFIG['VALIDATION']['MAX_FILE_SIZE']:
                raise ValueError("XML file size exceeds maximum allowed size")
            
            # Create submission record
            submission = MeFSubmission(
                user_id=data['user_id'],
                form_type=form_type,
                tax_year=data.get('tax_year', datetime.now().year),
                status=SubmissionStatus.PENDING,
                xml_content=xml_content,
                transmission_attempts=0,
                retry_count=0
            )

            if response.get('acknowledgment_xml'):
                ack_data = AcknowledgmentProcessor.process_acknowledgment(
                    response['acknowledgment_xml']
                )
                
                submission.status = self._map_irs_status(ack_data['status'])
                submission.acknowledgment_timestamp = datetime.fromisoformat(ack_data['timestamp'])
                submission.acknowledgment_data = response['acknowledgment_xml']
                
                if ack_data.get('errors'):
                    submission.error_message = str(ack_data['errors'])

            # Log submission attempt
            self.logger.info(f"Submission {submission.submission_id} transmitted to IRS")

            return {
                'success': True,
                'submission_id': submission.submission_id,
                'status': submission.status.value
            }

        except Exception as e:
            # Enhanced error handling
            error_message = f"Error submitting to IRS: {str(e)}"
            self.logger.error(error_message)
            
            submission.status = SubmissionStatus.ERROR
            submission.error_message = error_message
            submission.transmission_attempts += 1
            
            if submission.transmission_attempts >= MEF_CONFIG['TRANSMISSION']['MAX_RETRIES']:
                submission.status = SubmissionStatus.FAILED
                self.logger.error(f"Submission {submission.submission_id} failed after {submission.transmission_attempts} attempts")
            
            raise IrsSubmissionError(error_message)

    async def submit_1099_nec(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit 1099-NEC form"""
        try:
            # Validate form data
            errors = self.validation_rules.validate_1099_nec(data)
            if errors:
                return {
                    'success': False,
                    'errors': errors
                }
                
            # Validate schedule attachments
            attachment_validation = self.schedule_manager.validate_attachments(
                '1040', data.get('schedules', []))
            if not attachment_validation['is_valid']:
                return {'success': False, 'errors': attachment_validation}

            # Generate XML
            template = Form1099NECTemplate()
            xml_content = template.generate(data)
            
            # Validate schema
            schema_validation = self.schema_manager.validate_schema(
                xml_content, '1099_NEC')
            if not schema_validation['is_valid']:
                return {'success': False, 'errors': schema_validation['errors']}
                
            # Optimize XML
            optimized_xml = self.xml_optimizer.optimize(xml_content)
            
            # Validate XML
            validation_result = self.validator.validate_xml(optimized_xml, '1099_NEC')
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }
                
            # Sign XML
            signed_xml = self.xml_signer.sign_xml(optimized_xml)
            
            # Submit signed XML
            submission_result = await self._submit_to_irs(signed_xml, '1099_NEC', data)
            
            return submission_result
            
        except Exception as e:
            self.logger.error(f"Error submitting 1099-NEC: {str(e)}")
            raise

    async def submit_1099_k(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit 1099-K form"""
        try:
            # Validate form data
            errors = self.validation_rules.validate_1099_k(data)
            if errors:
                return {
                    'success': False,
                    'errors': errors
                }
                
            # Generate XML
            template = Form1099KTemplate()
            xml_content = template.generate(data)
            
            # Validate schema
            schema_validation = self.schema_manager.validate_schema(
                xml_content, '1099_K')
            if not schema_validation['is_valid']:
                return {'success': False, 'errors': schema_validation['errors']}
                
            # Optimize XML
            optimized_xml = self.xml_optimizer.optimize(xml_content)
            
            # Validate XML
            validation_result = self.validator.validate_xml(optimized_xml, '1099_K')
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }
                
            # Sign XML
            signed_xml = self.xml_signer.sign_xml(optimized_xml)
            
            # Submit signed XML
            submission_result = await self._submit_to_irs(signed_xml, '1099_K', data)
            
            return submission_result
            
        except Exception as e:
            self.logger.error(f"Error submitting 1099-K: {str(e)}")
            raise

    async def check_submission_status(self, submission_id: str) -> Dict[str, Any]:
        """Check status of a submission"""
        try:
            submission = MeFSubmission.query.filter_by(submission_id=submission_id).first()
            if not submission:
                return {
                    'success': False,
                    'error': 'Submission not found'
                }
                
            # Enhanced status checking with IRS
            irs_status = await self._check_irs_status(submission_id)
            
            if irs_status.get('acknowledgment_xml'):
                ack_data = AcknowledgmentProcessor.process_acknowledgment(
                    irs_status['acknowledgment_xml']
                )
                
                submission.status = self._map_irs_status(ack_data['status'])
                submission.acknowledgment_timestamp = datetime.fromisoformat(ack_data['timestamp'])
                
                if ack_data.get('errors'):
                    submission.error_message = str(ack_data['errors'])

            return {
                'success': True,
                'status': submission.status.value,
                'submitted_at': submission.submitted_at,
                'acknowledgment_timestamp': submission.acknowledgment_timestamp,
                'errors': submission.error_message if submission.error_message else None,
                'transmission_attempts': submission.transmission_attempts
            }
            
        except Exception as e:
            self.logger.error(f"Error checking submission status: {str(e)}")
            raise

    def _map_irs_status(self, irs_status: str) -> SubmissionStatus:
        """Map IRS status to internal status"""
        status_mapping = {
            'ACCEPTED': SubmissionStatus.ACCEPTED,
            'REJECTED': SubmissionStatus.REJECTED,
            'IN_PROCESS': SubmissionStatus.TRANSMITTED,
            'ERROR': SubmissionStatus.ERROR
        }
        return status_mapping.get(irs_status, SubmissionStatus.ERROR)

    async def _check_irs_status(self, submission_id: str) -> Dict[str, Any]:
        """Check submission status with IRS"""
        try:
            # TODO: Implement actual IRS API call here
            # This is a placeholder for the actual IRS API integration
            return {
                'status': 'ACCEPTED',
                'timestamp': datetime.utcnow().isoformat(),
                'acknowledgment_xml': '<Acknowledgment><Status>ACCEPTED</Status></Acknowledgment>'
            }
        except Exception as e:
            self.logger.error(f"Error checking IRS status: {str(e)}")
            raise
