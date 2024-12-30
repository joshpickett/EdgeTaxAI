from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from api.models.mef_submissions import MeFSubmission, SubmissionStatus
from api.services.mef.error_handler import MEFErrorHandler
from api.utils.error_handler import handle_api_error

class ErrorHandlingService:
    """Service for multi-level error checking and handling"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.mef_error_handler = MEFErrorHandler()
        
        # Define error severity levels
        self.severity_levels = {
            'CRITICAL': 1,
            'HIGH': 2,
            'MEDIUM': 3,
            'LOW': 4
        }
        
        # Define error categories
        self.error_categories = {
            'VALIDATION': {
                'max_retries': 2,
                'retry_delay': 1
            },
            'SUBMISSION': {
                'max_retries': 3,
                'retry_delay': 5
            },
            'SYSTEM': {
                'max_retries': 1,
                'retry_delay': 10
            }
        }

    async def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Handle errors with appropriate retry logic and logging"""
        try:
            error_info = self._categorize_error(error, category)
            
            # Log error details
            self._log_error(error_info, context)
            
            # Check if error is retryable
            if self._is_retryable(error_info, context):
                return await self._handle_retry(error_info, context)
            
            return await self._handle_failure(error_info, context)
            
        except Exception as e:
            self.logger.error(f"Error in error handling: {str(e)}")
            raise

    def _categorize_error(
        self,
        error: Exception,
        category: str
    ) -> Dict[str, Any]:
        """Categorize and enrich error information"""
        return {
            'type': type(error).__name__,
            'message': str(error),
            'category': category,
            'severity': self._determine_severity(error, category),
            'timestamp': datetime.utcnow().isoformat(),
            'is_retryable': self._check_retryable(error, category)
        }

    def _determine_severity(
        self,
        error: Exception,
        category: str
    ) -> str:
        """Determine error severity"""
        if category == 'SYSTEM':
            return 'CRITICAL'
        elif category == 'SUBMISSION':
            return 'HIGH'
        elif category == 'VALIDATION':
            return 'MEDIUM'
        return 'LOW'

    def _check_retryable(
        self,
        error: Exception,
        category: str
    ) -> bool:
        """Check if error type is retryable"""
        non_retryable = [
            'ValidationError',
            'AuthenticationError',
            'PermissionError'
        ]
        return type(error).__name__ not in non_retryable

    async def _handle_retry(
        self,
        error_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle error retry logic"""
        category_config = self.error_categories[error_info['category']]
        
        if context.get('retry_count', 0) >= category_config['max_retries']:
            return await self._handle_failure(error_info, context)
        
        context['retry_count'] = context.get('retry_count', 0) + 1
        
        return {
            'status': 'retry',
            'retry_count': context['retry_count'],
            'retry_delay': category_config['retry_delay'],
            'error_info': error_info
        }

    async def _handle_failure(
        self,
        error_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle error failure case"""
        if 'submission_id' in context:
            await self._update_submission_status(
                context['submission_id'],
                error_info
            )
        
        return {
            'status': 'failed',
            'error_info': error_info,
            'context': context
        }

    async def _update_submission_status(
        self,
        submission_id: str,
        error_info: Dict[str, Any]
    ) -> None:
        """Update submission status with error information"""
        try:
            submission = await MeFSubmission.get(submission_id)
            if submission:
                submission.status = SubmissionStatus.FAILED
                submission.error_message = error_info['message']
                submission.error_details = error_info
                await submission.save()
        except Exception as e:
            self.logger.error(f"Error updating submission status: {str(e)}")

    def _log_error(
        self,
        error_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """Log error with appropriate severity"""
        log_message = (
            f"Error: {error_info['type']} - {error_info['message']}\n"
            f"Category: {error_info['category']}\n"
            f"Severity: {error_info['severity']}\n"
            f"Context: {context}"
        )
        
        if error_info['severity'] == 'CRITICAL':
            self.logger.critical(log_message)
        elif error_info['severity'] == 'HIGH':
            self.logger.error(log_message)
        elif error_info['severity'] == 'MEDIUM':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _is_retryable(
        self,
        error_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if error should be retried"""
        if not error_info['is_retryable']:
            return False
            
        category_config = self.error_categories[error_info['category']]
        return context.get('retry_count', 0) < category_config['max_retries']
