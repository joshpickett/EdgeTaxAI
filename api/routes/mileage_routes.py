import os
import requests
import logging
from flask import Blueprint, request, jsonify, g
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from ..utils.error_handler import handle_api_error
from ..utils.db_utils import get_db_connection
from ..utils.validators import validate_location, validate_date
from ..utils.ai_utils import analyze_trip_purpose

# Constants
METERS_TO_MILES = 0.000621371
IRS_MILEAGE_RATE = float(os.getenv("IRS_MILEAGE_RATE", "0.655"))

# Enhanced business purpose validation
BUSINESS_PURPOSES = [
    "client meeting",
    "delivery",
    "work related",
    "business travel",
    "job site",
    "work event"
]

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
        
        # Cache the response
        if not hasattr(g, 'directions_cache'):
            g.directions_cache = {}
        cache_key = f"{start}-{end}"
        g.directions_cache[cache_key] = response.json()
        
        response.raise_for_status()
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
        purpose = data.get("purpose", "").strip()
        recurring = data.get('recurring', False)
        frequency = data.get('frequency')
        
        # Validate locations
        if not validate_location(start):
            return jsonify({"error": "Invalid start location format"}), 400
        if not validate_location(end):
            return jsonify({"error": "Invalid end location format"}), 400
        
        # Validate purpose
        if purpose:
            purpose_analysis = analyze_trip_purpose(purpose)
            if not purpose_analysis['is_business']:
                return jsonify({
                    "error": "Trip purpose does not appear to be business-related",
                    "suggestion": purpose_analysis['suggestion']
                }), 400

        # Fetch mileage using helper function
        distance, error = fetch_google_directions(start, end, os.getenv("GOOGLE_API_KEY"))
        if distance:
            # Calculate tax deduction
            distance_meters = float(distance.replace(" mi", "").replace(",", ""))
            distance_miles = distance_meters * METERS_TO_MILES
            tax_deduction = distance_miles * IRS_MILEAGE_RATE
            
            if recurring:
                # Handle recurring trip pattern
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO recurring_trips 
                    (user_id, start_location, end_location, frequency, purpose)
                    VALUES (?, ?, ?, ?, ?)
                """, (data.get("user_id"), start, end, frequency, purpose))
                
                # Schedule next occurrences
                schedule_recurring_trips(data.get("user_id"), start, end, frequency)

            return jsonify({
                "distance": distance,
                "tax_deduction": round(tax_deduction, 2)
            })
        else:
            return jsonify({"error": error}), 500

    except Exception as e:
        logging.error(f"Error calculating mileage: {str(e)}")
        return jsonify({"error": "Failed to calculate mileage"}), 500

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

@mileage_bp.route("/mileage/bulk", methods=["POST"])
def bulk_mileage_upload():
    """Handle bulk mileage record uploads."""
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid JSON payload"}), 400
            
        data = request.json
        records = data.get("records", [])
        
        if not records:
            return jsonify({"error": "No records provided"}), 400
            
        successful_records = []
        failed_records = []
        
        for record in records:
            try:
                # Validate record
                if not all(k in record for k in ["start", "end", "date"]):
                    failed_records.append({
                        "record": record,
                        "error": "Missing required fields"
                    })
                    continue
                    
                # Calculate distance
                distance, error = fetch_google_directions(
                    record["start"], 
                    record["end"], 
                    os.getenv("GOOGLE_API_KEY")
                )
                
                if error:
                    failed_records.append({"record": record, "error": error})
                    continue
                    
                successful_records.append({
                    "record": record,
                    "distance": distance
                })
                
            except Exception as e:
                failed_records.append({
                    "record": record,
                    "error": str(e)
                })
                
        return jsonify({
            "success": len(successful_records),
            "failed": len(failed_records),
            "successful_records": successful_records,
            "failed_records": failed_records
        }), 200
        
    except Exception as e:
        logging.error(f"Error processing bulk mileage upload: {e}")
        return jsonify({"error": "Failed to process bulk upload"}), 500

@mileage_bp.route("/mileage/recurring", methods=["POST"])
def add_recurring_trip():
    """Add a recurring trip pattern."""
    try:
        data = request.json
        user_id = data.get("user_id")
        start = data.get("start")
        end = data.get("end")
        frequency = data.get("frequency")  # daily, weekly, monthly
        purpose = data.get("purpose")
        
        if not all([user_id, start, end, frequency, purpose]):
            return jsonify({"error": "Missing required fields"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO recurring_trips 
            (user_id, start_location, end_location, frequency, purpose)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, start, end, frequency, purpose))
        
        conn.commit()
        
        return jsonify({
            "message": "Recurring trip added successfully",
            "trip_id": cursor.lastrowid
        }), 201
        
    except Exception as e:
        logging.error(f"Error adding recurring trip: {str(e)}")
        return jsonify({"error": "Failed to add recurring trip"}), 500
