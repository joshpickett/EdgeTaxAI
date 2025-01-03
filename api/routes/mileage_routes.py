import os
import sys
from flask import Blueprint, request, jsonify
from api.services.mileage_service import MileageService
from api.config.database import SessionLocal
from api.utils.error_handler import handle_api_error
from api.utils.rate_limit import rate_limit

# Initialize cache manager
# Configure Logging
# Blueprint for mileage-related routes
mileage_bp = Blueprint("mileage", __name__)


@mileage_bp.route("/mileage", methods=["POST"])
@rate_limit(requests_per_minute=60)
@handle_api_error
def calculate_mileage() -> Tuple[Dict[str, Any], int]:
    """
    Calculate mileage between two locations using Google Maps API.
    Returns distance and estimated travel time.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid JSON payload"}), 400

    try:
        data = request.json
        start = data.get("start", "").strip()
        end = data.get("end", "").strip()
        purpose = data.get("purpose", "").strip()

        # Check cache first
        cache_key = f"mileage:{start}:{end}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        result = trip_analyzer.calculate_trip_distance(request.json)
        cache_manager.set(cache_key, result, timeout=86400)  # Cache for 24 hours
        return result

    except Exception as e:
        raise APIError(f"Failed to calculate mileage: {str(e)}", status_code=500)


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

        with SessionLocal() as db:
            service = MileageService(db)
            mileage, expense, deduction = service.create_mileage_record(data)

        return (
            jsonify(
                {
                    "message": "Mileage record added successfully",
                    "data": {"distance": mileage.distance, "date": date},
                }
            ),
            201,
        )
    except Exception as e:
        logging.error(f"Error adding mileage record: {e}")
        return jsonify({"error": "Failed to add mileage record"}), 500


@mileage_bp.route("/mileage/bulk", methods=["POST"])
@rate_limit(requests_per_minute=30)
@handle_api_error
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
                    failed_records.append(
                        {"record": record, "error": "Missing required fields"}
                    )
                    continue

                # Calculate distance
                distance, error = trip_analyzer.fetch_google_directions(
                    record["start"], record["end"]
                )

                if error:
                    failed_records.append({"record": record, "error": error})
                    continue

                successful_records.append({"record": record, "distance": distance})

            except Exception as e:
                failed_records.append({"record": record, "error": str(e)})

        return (
            jsonify(
                {
                    "success": len(successful_records),
                    "failed": len(failed_records),
                    "successful_records": successful_records,
                    "failed_records": failed_records,
                }
            ),
            200,
        )

    except Exception as e:
        raise APIError(f"Failed to process bulk upload: {str(e)}", status_code=500)


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

        cursor.execute(
            """
            INSERT INTO recurring_trips 
            (user_id, start_location, end_location, frequency, purpose)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, start, end, frequency, purpose),
        )

        conn.commit()

        return (
            jsonify(
                {
                    "message": "Recurring trip added successfully",
                    "trip_id": cursor.lastrowid,
                }
            ),
            201,
        )

    except Exception as e:
        logging.error(f"Error adding recurring trip: {str(e)}")
        return jsonify({"error": "Failed to add recurring trip"}), 500


@mileage_bp.route("/mileage/summary", methods=["GET"])
@cache_response(timeout=3600)  # Cache for 1 hour
@handle_api_error
def get_mileage_summary():
    """Get mileage summary with tax implications"""
    try:
        user_id = request.args.get("user_id")
        year = request.args.get("year", datetime.now().year)

        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total mileage
        cursor.execute(
            """
            SELECT SUM(distance) as total_miles,
                   COUNT(*) as total_trips
            FROM mileage
            WHERE user_id = ?
            AND strftime('%Y', date) = ?
        """,
            (user_id, str(year)),
        )

        result = cursor.fetchone()
        total_miles = result[0] or 0
        total_trips = result[1] or 0

        # Calculate tax deduction
        tax_deduction = total_miles * IRS_MILEAGE_RATE

        return (
            jsonify(
                {
                    "year": year,
                    "total_miles": total_miles,
                    "total_trips": total_trips,
                    "tax_deduction": tax_deduction,
                    "rate_used": IRS_MILEAGE_RATE,
                    "last_updated": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        logging.error(f"Error getting mileage summary: {e}")
        return jsonify({"error": str(e)}), 500


@mileage_bp.route("/mileage/export", methods=["GET"])
def export_mileage():
    """Export mileage records in various formats"""
    try:
        user_id = request.args.get("user_id")
        format_type = request.args.get("format", "csv")
        year = request.args.get("year", datetime.now().year)

        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT date, start_location, end_location, 
                   distance, purpose
            FROM mileage
            WHERE user_id = ?
            AND strftime('%Y', date) = ?
            ORDER BY date DESC
        """,
            (user_id, str(year)),
        )

        records = cursor.fetchall()

        if format_type == "csv":
            output = io.StringIO()
            df = pd.DataFrame(
                records,
                columns=[
                    "Date",
                    "Start Location",
                    "End Location",
                    "Distance",
                    "Purpose",
                ],
            )
            df.to_csv(output, index=False)
            output.seek(0)

            return send_file(
                io.BytesIO(output.getvalue().encode("utf-8")),
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"mileage_records_{year}.csv",
            )

        return jsonify({"error": "Unsupported format"}), 400

    except Exception as e:
        logging.error(f"Error exporting mileage: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(mileage_bp)
    app.run(debug=True)
