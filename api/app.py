from flask import Flask
from flask_cors import CORS
from routes.auth_routes import auth_bp
from routes.expense_routes import expense_bp
from routes.reports_routes import reports_bp
from routes.bank_routes import bank_bp
from routes.tax_routes import tax_bp
import logging

# Configure Logging
logging.basicConfig(
    filename="api_startup.log",  # Log file for API startup and routes
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_app():
    """
    Factory function to create the Flask app.
    """
    app = Flask(__name__)
    CORS(app)  # Enable Cross-Origin Resource Sharing for frontend requests

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(expense_bp, url_prefix="/api/expenses")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(bank_bp, url_prefix="/api/banks")
    app.register_blueprint(tax_bp, url_prefix="/api/tax")

    # Log API Startup
    log_api_startup(app)
    return app

def log_api_startup(app):
    """
    Logs all registered routes and startup information.
    """
    logging.info("Starting Flask API Server...")
    logging.info("Registered Endpoints:")

    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":  # Exclude static files
            methods = ','.join(rule.methods - {"HEAD", "OPTIONS"})
            logging.info(f"{rule.endpoint} → {rule.rule} [{methods}]")

    logging.info("Flask API Server started successfully.")

if __name__ == "__main__":
    app = create_app()
    port = 5000
    logging.info(f"Running API server on http://127.0.0.1:{port}")
    app.run(debug=True, port=port)
