import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from typing import Dict, Any, Optional
from datetime import datetime
import json

class ResponseFormatter:
    @staticmethod
    def format_response(data: Any, 
                       status: str = "success", 
                       message: Optional[str] = None, 
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format Application Programming Interface response with consistent structure
        """
        response = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        if message:
            response["message"] = message
            
        if metadata:
            response["metadata"] = metadata
            
        return response

    @staticmethod
    def format_error(message: str, 
                    error_code: Optional[str] = None, 
                    details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format error response with consistent structure
        """
        error_response = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": {
                "message": message
            }
        }
        
        if error_code:
            error_response["error"]["code"] = error_code
            
        if details:
            error_response["error"]["details"] = details
            
        return error_response

    @staticmethod
    def format_batch_response(batch_id: str,
                            total: int,
                            processed: int,
                            failed: int,
                            results: list,
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format batch processing response
        """
        response = {
            "status": "success" if failed == 0 else "partial_success",
            "timestamp": datetime.now().isoformat(),
            "batch_id": batch_id,
            "summary": {
                "total": total,
                "processed": processed,
                "failed": failed,
                "success_rate": (processed - failed) / total if total > 0 else 0
            },
            "results": results
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response
