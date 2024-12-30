import uuid
from datetime import datetime
from typing import Dict, Any

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: Dict[str, Any] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
        self.error_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
        self.context = {}

    def add_context(self, context: Dict[str, Any]):
        self.context.update(context)
        self.logger.error(f"Error {self.error_id}: {self.message}", extra={
            'error_id': self.error_id,
            'context': self.context,
            'timestamp': self.timestamp
        })

    # ...rest of the code...

class ErrorHandler:
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle and format error response"""
        if isinstance(error, APIError):
            return self._handle_api_error(error, context)

        return self._handle_generic_error(error, context)

    # ...rest of the code...
