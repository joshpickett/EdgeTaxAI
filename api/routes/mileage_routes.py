import os
import requests
from flask import Blueprint, request, jsonify

# Blueprint for mileage-related routes
mileage_bp = Blueprint("mileage", __name__)

def fetch_google_directions(start, end, api_key):
    """
    Fetch mileage from Google Directions API.
    """
    try:
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for non-200 HTTP status
        google_data = response.json()

        if google_data.get("status") == "OK":
            return google_data["routes"][0]["legs"][0]["distance"]["text"]
        else:
            return None, google_data.get("error_message", "Unknown error from Google API")
    except Exception as e:
        return None, str(e)

@mileage_bp.route("/mileage", methods=["POST"])
def calculate_mileage():
    """
    Calculate mileage between two locations using Google Directions API.
    """
    try:
        # Extract request data
        data = request.json
        start = data.get("start", "").strip()
        end = data.get("end", "").strip()

        if not start or not end:
            return jsonify({"error": "Both start and end locations are required."}), 400

        # Load Google API Key from environment variables
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            return jsonify({"error": "Google API key not configured."}), 500

        # Fetch mileage using helper function
        distance, error = fetch_google_directions(start, end, GOOGLE_API_KEY)
        if distance:
            return jsonify({"distance": distance})
        else:
            return jsonify({"error": error}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
