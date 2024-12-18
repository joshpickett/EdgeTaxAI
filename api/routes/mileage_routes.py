import os
import requests
from flask import Blueprint, request, jsonify

# Blueprint for mileage-related routes
mileage_bp = Blueprint("mileage", __name__)

@mileage_bp.route("/mileage", methods=["POST"])
def calculate_mileage():
    """
    Calculate mileage between two locations using Google Directions API.
    """
    try:
        # Extract request data
        data = request.json
        start = data.get("start")
        end = data.get("end")

        if not start or not end:
            return jsonify({"error": "Both start and end locations are required."}), 400

        # Load Google API Key from environment variables
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            return jsonify({"error": "Google API key not configured."}), 500

        # Send request to Google Directions API
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={GOOGLE_API_KEY}"
        response = requests.get(url)
        google_data = response.json()

        # Handle Google API response
        if google_data.get("status") == "OK":
            distance = google_data["routes"][0]["legs"][0]["distance"]["text"]
            return jsonify({"distance": distance})
        else:
            return jsonify({"error": google_data.get("error_message", "Failed to fetch mileage.")}), 500

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
