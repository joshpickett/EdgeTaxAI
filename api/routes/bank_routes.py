import os
import sys
from api.setup_path import setup_python_path

# Set up path for both package and direct execution
if __name__ == "__main__":
    setup_python_path(__file__)
else:
    setup_python_path()

from flask import Blueprint, request, jsonify

# ...rest of the code...

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(bank_bp)
    app.run(debug=True)
