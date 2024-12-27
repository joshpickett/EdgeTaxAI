import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from flask import Blueprint, request, jsonify
from api.utils.gig_platform_processor import GigPlatformProcessor
from api.utils.error_handler import handle_api_error

# ...rest of the code...

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(gig_bp)
    app.run(debug=True)
