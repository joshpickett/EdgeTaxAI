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
                return jsonify({"error": "No session ID provided"}), HTTPStatus.UNAUTHORIZED

            session = session_manager.get_session(session_id)
            if not session:
                audit_logger.log_security_event(
                    event_type="invalid_session",
                    details={"session_id": session_id}
                )
                return jsonify({"error": "Invalid session"}), HTTPStatus.UNAUTHORIZED

            return f(*args, **kwargs)

        return decorated_function

    return decorator
