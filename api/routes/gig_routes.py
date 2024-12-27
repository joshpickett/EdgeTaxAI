from flask import Blueprint, request, jsonify, redirect
import logging
import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from ..utils.retry_handler import with_retry
from ..utils.gig_platform_processor import GigPlatformProcessor
from ..services.gig_platform_service import GigPlatformService
from ..utils.validators import validate_user_id, validate_platform
from ..utils.error_handler import handle_api_error, handle_platform_error

# Initialize Blueprint
gig_routes = Blueprint('gig', __name__, url_prefix='/api/gig')

# Initialize services
gig_platform_service = GigPlatformService()

# Configure Logging
logging.basicConfig(
    filename="gig_platform.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Simulated in-memory storage for tokens and connections
USER_TOKENS = {}
USER_CONNECTIONS = {}

# Valid platforms for OAuth connections
VALID_PLATFORMS = {"uber", "lyft", "doordash", "instacart", "upwork", "fiverr"}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth configuration
OAUTH_CONFIG = {
    'uber': {
        'token_url': 'https://login.uber.com/oauth/v2/token',
        'auth_url': 'https://login.uber.com/oauth/v2/authorize'
    },
    'lyft': {
        'token_url': 'https://api.lyft.com/oauth/token',
        'auth_url': 'https://www.lyft.com/oauth/authorize'
    }
}

@with_retry(max_attempts=3, initial_delay=1.0)
@gig_routes.route("/gig/connect/<platform>", methods=["GET"])
def connect_platform(platform):
    try:
        return gig_platform_service.connect_platform(platform.lower(), request.args.get("user_id"))
    except Exception as e:
        return handle_platform_error(e)

@with_retry(max_attempts=3, initial_delay=1.0)
@gig_routes.route("/gig/callback", methods=["POST"])
def oauth_callback():
    data = request.json
    user_id = data.get("user_id")
    platform = data.get("platform")
    code = data.get("code")

    try:
        if not validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        if not validate_platform(platform):
            raise ValueError(f"Invalid platform: {platform}")

        if not code:
            raise ValueError("Authorization code is required.")

        # Simulate token exchange
        access_token = f"token_for_{platform}_{code}"
        USER_TOKENS[user_id] = USER_TOKENS.get(user_id, {})
        USER_TOKENS[user_id][platform] = access_token

        logger.info(f"Token successfully stored for user {user_id} on platform {platform}.")
        
        # Use platform service to handle data processing
        processed_data = gig_platform_service.process_platform_data(platform, access_token)
        gig_platform_service.store_platform_data(user_id, platform, processed_data)
        
        return jsonify({"message": "OAuth successful", "platform": platform}), 200
    except ValueError as e:
        return handle_api_error(APIError(str(e), 400))
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        return jsonify({"error": "OAuth callback failed"}), 500

@with_retry(max_attempts=3, initial_delay=1.0)
@gig_routes.route("/gig/connections", methods=["GET"])
def list_connections():
    user_id = request.args.get("user_id")
    try:
        if not validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        connections = USER_CONNECTIONS.get(user_id, [])
        logger.info(f"Retrieved connections for user {user_id}.")
        return jsonify({"connections": connections}), 200
    except ValueError as e:
        return handle_api_error(APIError(str(e), 400))
    except Exception as e:
        logger.error(f"Failed to fetch connections: {str(e)}")
        return jsonify({"error": "Failed to fetch connections"}), 500

@with_retry(max_attempts=3, initial_delay=1.0)
@gig_routes.route("/gig/fetch-data", methods=["GET"])
def fetch_data():
    user_id = request.args.get("user_id")
    platform = request.args.get("platform")

    try:
        # Validate inputs
        if not validate_user_id(user_id):
            raise ValueError("Invalid user ID")
        if not validate_platform(platform):
            raise ValueError(f"Invalid platform: {platform}")

        # Check if the platform is connected
        token = USER_TOKENS.get(user_id, {}).get(platform)
        if not token:
            raise ValueError(f"No access token found for platform: {platform}")

        # Simulate data retrieval
        data = {"platform": platform, "data": f"Sample data for {platform}"}
        logger.info(f"Fetched data for user {user_id} on platform {platform}.")
        return jsonify(data), 200
    except ValueError as e:
        return handle_api_error(APIError(str(e), 400))
    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
        return jsonify({"error": "Failed to fetch data"}), 500

@with_retry(max_attempts=3, initial_delay=1.0)
@gig_routes.route("/gig/exchange-token", methods=["POST"])
def exchange_token():
    """Exchange OAuth code for access token."""
    try:
        data = request.json
        platform = data.get("platform")
        code = data.get("code")
        
        if not platform or not code:
            return jsonify({"error": "Platform and code are required"}), 400
            
        token_response = gig_platform_service.exchange_oauth_code(platform, code)
        return jsonify({"access_token": token_response.get("access_token")}), 200
    except Exception as e:
        logging.error(f"Token exchange error: {str(e)}")
        return jsonify({"error": "Failed to exchange token"}), 500

@with_retry(max_attempts=3, initial_delay=1.0)
@gig_routes.route("/refresh-token", methods=["POST"])
def refresh_token():
    """Refresh OAuth token for platform"""
    try:
        data = request.json
        user_id = data.get("user_id")
        platform = data.get("platform")
        
        if not all([user_id, platform]):
            return jsonify({"error": "Missing required parameters"}), 400
            
        # Get refresh token
        refresh_token = USER_TOKENS.get(user_id, {}).get(f"{platform}_refresh")
        if not refresh_token:
            return jsonify({"error": "No refresh token found"}), 404
            
        # Get platform config
        platform_config = OAUTH_CONFIG.get(platform)
        if not platform_config:
            return jsonify({"error": "Platform not supported"}), 400
            
        # Request new token
        response = requests.post(
            platform_config["token_url"],
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": os.getenv(f"{platform.upper()}_CLIENT_ID"),
                "client_secret": os.getenv(f"{platform.upper()}_CLIENT_SECRET")
            }
        )
        
        if response.status_code == 200:
            new_tokens = response.json()
            # Update stored tokens
            if user_id not in USER_TOKENS:
                USER_TOKENS[user_id] = {}
            USER_TOKENS[user_id][platform] = new_tokens["access_token"]
            if "refresh_token" in new_tokens:
                USER_TOKENS[user_id][f"{platform}_refresh"] = new_tokens["refresh_token"]
                
            return jsonify({"message": "Token refreshed successfully"}), 200
        else:
            return jsonify({"error": "Failed to refresh token"}), response.status_code
            
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        return jsonify({"error": "Failed to refresh token"}), 500

@gig_routes.route("/gig/sync/<platform>", methods=["POST"])
def sync_platform_data(platform):
    """Sync data from specific gig platform"""
    try:
        data = request.json
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
            
        # Use the gig_platform_service instance to fetch data
        sync_result = gig_platform_service.sync_platform_data(platform, user_id)
        
        return jsonify({
            "status": "success",
            "synced_data": sync_result
        }), 200
    except Exception as e:
        logging.error(f"Platform sync error: {e}")
        return jsonify({"error": str(e)}), 500

@gig_routes.route("/gig/earnings", methods=["GET"])
def get_earnings():
    """Get earnings data from all connected platforms"""
    try:
        user_id = request.args.get("user_id")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
            
        earnings_data = {}
        for platform in USER_CONNECTIONS.get(user_id, []):
            platform_earnings = gig_platform_service.get_platform_earnings(
                platform,
                user_id,
                start_date,
                end_date
            )
            earnings_data[platform] = platform_earnings
            
        return jsonify(earnings_data), 200
    except Exception as e:
        logging.error(f"Error fetching earnings: {e}")
        return jsonify({"error": str(e)}), 500
