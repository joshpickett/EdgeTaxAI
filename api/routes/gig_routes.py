from flask import Blueprint, request, jsonify, redirect
import logging
import os
import requests
from typing import Optional, Dict, Any
from ..utils.api_config import APIConfig
from ..utils.error_handler import handle_api_error, handle_validation_error
from ..utils.validators import validate_platform, validate_user_id

# Configure Logging
logging.basicConfig(
    filename="gig_platform.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Platform OAuth Configuration
OAUTH_URLS = {
    "uber": "https://login.uber.com/oauth/v2/authorize",
    "lyft": "https://api.lyft.com/oauth/authorize",
    "upwork": "https://www.upwork.com/ab/account-security/oauth2/authorize"
}

gig_routes = Blueprint("gig_routes", __name__)

# Simulated in-memory storage for tokens and connections
USER_TOKENS = {}
USER_CONNECTIONS = {}

# Valid platforms for OAuth connections
VALID_PLATFORMS = {"uber", "lyft", "doordash", "instacart", "upwork", "fiverr"}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_oauth_url(platform: str) -> Optional[str]:
    """Get OAuth URL for platform with proper configuration."""
    try:
        platform_url = APIConfig.get_gig_platform_url(platform, "oauth")
        if not platform_url:
            logging.warning(f"No OAuth URL configured for platform: {platform}")
            return None
            
        client_id = os.getenv(f'{platform.upper()}_CLIENT_ID')
        if not client_id:
            logging.error(f"Missing client ID for platform: {platform}")
            return None
            
        oauth_url = f"{platform_url}?client_id={client_id}"
        logging.info(f"Generated OAuth URL for {platform}: {oauth_url}")
        return oauth_url
    except Exception as e:
        logging.error(f"Error generating OAuth URL for {platform}: {e}")
        return None

@gig_routes.route("/gig/connect/<platform>", methods=["GET"])
def connect_platform(platform):
    try:
        platform = platform.lower()
        if not validate_platform(platform):
            logging.error(f"Invalid platform specified: {platform}")
            return jsonify({"error": f"Invalid platform: {platform}"}), 400
            
        oauth_url = get_oauth_url(platform)
        if not oauth_url:
            logging.error(f"Failed to generate OAuth URL for platform: {platform}")
            return jsonify({"error": "Failed to generate OAuth URL"}), 400
            
        logging.info(f"Redirecting to OAuth URL for {platform}: {oauth_url}")
        return redirect(oauth_url)
    except Exception as e:
        logging.error(f"Error in platform connection: {str(e)}")
        return jsonify({"error": "Failed to connect platform"}), 500

@gig_routes.route("/gig/callback", methods=["POST"])
def oauth_callback():
    data = request.json
    user_id = data.get("user_id")
    platform = data.get("platform")
    code = data.get("code")

    try:
        # Validate inputs
        user_id = validate_user_id(user_id)
        validate_platform(platform)

        if not code:
            raise ValueError("Authorization code is required.")

        # Simulate token exchange
        access_token = f"token_for_{platform}_{code}"
        USER_TOKENS[user_id] = USER_TOKENS.get(user_id, {})
        USER_TOKENS[user_id][platform] = access_token

        logger.info(f"Token successfully stored for user {user_id} on platform {platform}.")
        return jsonify({"message": "OAuth successful", "platform": platform}), 200
    except ValueError as e:
        return handle_validation_error(str(e))
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        return jsonify({"error": "OAuth callback failed"}), 500

@gig_routes.route("/gig/connections", methods=["GET"])
def list_connections():
    user_id = request.args.get("user_id")
    try:
        user_id = validate_user_id(user_id)
        connections = USER_CONNECTIONS.get(user_id, [])
        logger.info(f"Retrieved connections for user {user_id}.")
        return jsonify({"connections": connections}), 200
    except ValueError as e:
        return handle_validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to fetch connections: {str(e)}")
        return jsonify({"error": "Failed to fetch connections"}), 500

@gig_routes.route("/gig/fetch-data", methods=["GET"])
def fetch_data():
    user_id = request.args.get("user_id")
    platform = request.args.get("platform")

    try:
        # Validate inputs
        user_id = validate_user_id(user_id)
        validate_platform(platform)

        # Check if the platform is connected
        token = USER_TOKENS.get(user_id, {}).get(platform)
        if not token:
            raise ValueError(f"No access token found for platform: {platform}")

        # Simulate data retrieval
        data = {"platform": platform, "data": f"Sample data for {platform}"}
        logger.info(f"Fetched data for user {user_id} on platform {platform}.")
        return jsonify(data), 200
    except ValueError as e:
        return handle_validation_error(str(e))
    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
        return jsonify({"error": "Failed to fetch data"}), 500

@gig_routes.route("/gig/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange OAuth code for access token."""
    try:
        data = request.json
        platform = data.get("platform")
        code = data.get("code")
        
        if not platform or not code:
            return jsonify({"error": "Platform and code are required"}), 400
            
        # Exchange code for token using platform-specific OAuth endpoints
        token_response = exchange_oauth_code(platform, code)
        return jsonify({"access_token": token_response.get("access_token")}), 200
    except Exception as e:
        logging.error(f"Token exchange error: {str(e)}")
        return jsonify({"error": "Failed to exchange token"}), 500
