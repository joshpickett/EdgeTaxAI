from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Import and register blueprints
    from .routes.gig_routes import gig_routes
    app.register_blueprint(gig_routes)
    
    return app
