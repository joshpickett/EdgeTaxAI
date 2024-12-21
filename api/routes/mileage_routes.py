import os
import requests
import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from ..utils.error_handler import handle_api_error
from ..utils.db_utils import get_db_connection

# Configure Logging
logging.basicConfig(
    filename="mileage.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint for mileage-related routes
mileage_bp = Blueprint("mileage", __name__)

def fetch_google_directions(start: str, end: str, api_key: str) -> tuple[Optional[str], Optional[str]]:
    """
    Fetch mileage from Google Directions API.
    """
    try:
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={api_key}"
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for non-200 HTTP status
        google_data = response.json()

        if google_data.get("status") == "OK":
            return google_data["routes"][0]["legs"][0]["distance"]["text"], None
        else:
            return None, google_data.get("error_message", "Unknown error from Google API")
    except Exception as e:
        return None, str(e)

@mileage_bp.route("/mileage", methods=["POST"])
def calculate_mileage() -> Tuple[Dict[str, Any], int]:
    """
    Calculate mileage between two locations using Google Maps API.
    Returns distance and estimated travel time.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid JSON payload"}), 400
        
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

@mileage_bp.route("/mileage/add", methods=["POST"])
def add_mileage_record():
    """Add a new mileage record to the database."""
    try:
        data = request.json
        required_fields = ["user_id", "start_location", "end_location", "date"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        user_id = data.get("user_id")
        start_location = data.get("start_location")
        end_location = data.get("end_location")
        date = data.get("date")
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Calculate distance using Google Maps API
        distance, error = fetch_google_directions(start_location, end_location, os.getenv("GOOGLE_API_KEY"))
        if error:
            return jsonify({"error": f"Failed to calculate distance: {error}"}), 500

        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO mileage (user_id, start_location, end_location, distance, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, start_location, end_location, distance, date)
        )
        conn.commit()
        conn.close()

        return jsonify({
            "message": "Mileage record added successfully",
            "data": {"distance": distance, "date": date}
        }), 201
    except Exception as e:
        logging.error(f"Error adding mileage record: {e}")
        return jsonify({"error": "Failed to add mileage record"}), 500
