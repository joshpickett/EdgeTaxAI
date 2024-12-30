from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from api.services.error_handling_service import ErrorHandlingService
from api.models.mef_submissions import MeFSubmission, SubmissionStatus
from api.services.security.alert_manager import AlertManager

class MEFErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_service = ErrorHandlingService()
        self.alert_manager = AlertManager()
        self.retry_limits = {
            'transmission': 3,
            'validation': 2,
            'acknowledgment': 3
        }

    async def handle_submission_error(self, 
                                    submission: MeFSubmission, 
                                    error: Exception) -> Dict[str, Any]:
        """Enhanced submission error handling with multi-level checks"""
        try:
            context = {
                'submission_id': submission.submission_id,
                'retry_count': submission.retry_count,
                'form_type': submission.form_type
            }
             
            error_result = await self.error_service.handle_error(
                error,
                context,
                'SUBMISSION'
            )
             
            return await self._handle_failure(submission, error_result['error_info'])
            
        except Exception as e:
            self.logger.error(f"Error handling submission error: {str(e)}")
            raise

    async def _handle_retry(self, 
                          submission: MeFSubmission, 
                          error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle submission retry"""
        submission.retry_count += 1
        submission.status = SubmissionStatus.PENDING
        submission.error_details = error_details
        
        await self._log_retry_attempt(submission)
        
        return {
            'status': 'retry',
            'retry_count': submission.retry_count,
            'next_attempt': self._calculate_next_attempt(submission)
        }

    async def _handle_failure(self, 
                            submission: MeFSubmission, 
                            error_details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle submission failure"""
        submission.status = SubmissionStatus.FAILED
        submission.error_details = error_details
        
        await self._log_failure(submission)
        await self._notify_failure(submission)
        
        return {
            'status': 'failed',
            'error': error_details,
            'submission_id': submission.submission_id
        }

    def _categorize_error(self, error: Exception) -> Dict[str, Any]:
        """Categorize the error type and details"""
        return {
            'type': type(error).__name__,
            'message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'category': self._determine_error_category(error)
        }

    def _should_retry(self, 
                     submission: MeFSubmission, 
                     error_details: Dict[str, Any]) -> bool:
        """Determine if submission should be retried"""
        if submission.retry_count >= self.retry_limits[error_details['category']]:
            return False
            
        return error_details['category'] in ['transmission', 'validation']

    async def _log_retry_attempt(self, submission: MeFSubmission) -> None:
        """Log retry attempt details"""
        self.logger.info(
            f"Retry attempt {submission.retry_count} for submission {submission.submission_id}"
        )

    async def _log_failure(self, submission: MeFSubmission) -> None:
        """Log submission failure details"""
        self.logger.error(
            f"Submission {submission.submission_id} failed after {submission.retry_count} retries"
        )

    async def _notify_failure(self, submission: MeFSubmission) -> None:
        """Notify relevant parties of submission failure"""
        await self.alert_manager.trigger_alert(
            alert_type='submission_failure',
            severity='HIGH',
            details={
                'submission_id': submission.submission_id,
                'error_details': submission.error_details,
                'retry_count': submission.retry_count
            }
        )

    def _determine_error_category(self, error: Exception) -> str:
        """Determine error category for retry logic"""
        error_type = type(error).__name__
        
        if error_type in ['ConnectionError', 'Timeout']:
            return 'transmission'
        elif error_type in ['ValidationError', 'SchemaError']:
            return 'validation'
        elif error_type in ['AcknowledgmentError']:
            return 'acknowledgment'
            
        return 'unknown'

    def _calculate_next_attempt(self, submission: MeFSubmission) -> str:
        """Calculate next retry attempt time"""
        delay = min(300 * (2 ** (submission.retry_count - 1)), 3600)
        next_attempt = datetime.utcnow() + timedelta(seconds=delay)
        return next_attempt.isoformat()
