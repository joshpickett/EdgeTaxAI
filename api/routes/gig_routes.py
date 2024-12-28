import os
import sys
from api.setup_path import setup_python_path
setup_python_path(__file__)

from flask import Blueprint, request, jsonify, g
from api.utils.gig_platform_processor import GigPlatformProcessor
from api.utils.error_handler import handle_api_error
from api.utils.session_manager import SessionManager
from api.utils.token_manager import TokenManager

# Initialize managers
session_manager = SessionManager()
token_manager = TokenManager()

# ...rest of the code...

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(gig_bp)
    app.run(debug=True)
