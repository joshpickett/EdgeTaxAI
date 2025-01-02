from functools import wraps
from flask import request, jsonify
from http import HTTPStatus
from api.utils.session_manager import SessionManager
from api.utils.audit_logger import AuditLogger

session_manager = SessionManager()
audit_logger = AuditLogger()


def validate_session():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_id = request.headers.get("Session-Id")
            if not session_id:
                return (
                    jsonify({"error": "No session ID provided"}),
                    HTTPStatus.UNAUTHORIZED,
                )

            if not session_manager.validate_session(session_id):
                audit_logger.log_security_event(
                    user_id=None,
                    event_type="invalid_session",
                    ip_address=request.remote_addr,
                    details={"session_id": session_id},
                )
                return (
                    jsonify({"error": "Invalid or expired session"}),
                    HTTPStatus.UNAUTHORIZED,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator
