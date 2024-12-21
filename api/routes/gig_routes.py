from flask import Blueprint, request, jsonify, redirect
import logging

gig_routes = Blueprint("gig_routes", __name__)

# Simulated in-memory storage for tokens and connections
USER_TOKENS = {}
USER_CONNECTIONS = {}

# Valid platforms for OAuth connections
VALID_PLATFORMS = {"uber", "lyft", "doordash", "instacart", "upwork", "fiverr"}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_platform(platform):
    """Validate the platform parameter."""
    if platform not in VALID_PLATFORMS:
        raise ValueError("Invalid platform specified.")

def validate_user_id(user_id):
    """Validate user_id as an integer."""
    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise ValueError("User ID must be a valid integer.")

@gig_routes.route("/gig/connect/<platform>", methods=["GET"])
def connect_platform(platform):
    try:
        validate_platform(platform.lower())
        # Simulate generating OAuth URL
        oauth_url = f"https://{platform}.com/oauth/authorize"
        logger.info(f"Redirecting to OAuth URL for platform: {platform}")
        return redirect(oauth_url)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

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
        return jsonify({"error": str(e)}), 400
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
        return jsonify({"error": str(e)}), 400
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
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Failed to fetch data: {str(e)}")
        return jsonify({"error": "Failed to fetch data"}), 500
