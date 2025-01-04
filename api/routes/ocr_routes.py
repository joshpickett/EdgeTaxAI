from flask import Blueprint, request, jsonify
from ..controllers.ocr_controller import OCRController
from ..utils.error_handler import handle_api_error
from ..utils.rate_limit import rate_limit
from ..config import Config
import logging

ocr_bp = Blueprint("ocr", __name__)
ocr_controller = OCRController()

@ocr_bp.route("/analyze-receipt", methods=["POST"])
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT["DEFAULT"])
async def analyze_receipt():
    """Analyze receipt image and extract structured data."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        user_id = request.headers.get("X-User-ID")

        if not ocr_controller.validate_receipt(file.read(), file.filename):
            return jsonify({"error": "Invalid file type"}), 400
        file.seek(0)

        result = await ocr_controller.handle_receipt_processing(file.read(), user_id)
        return jsonify(result), 200

    except Exception as e:
        return handle_api_error(e)

@ocr_bp.route("/extract-expense", methods=["POST"])
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT["DEFAULT"])
def extract_expense():
    """Extract expense information from receipt text."""
    try:
        data = request.json
        receipt_text = data.get("text")

        if not receipt_text:
            return jsonify({"error": "Receipt text is required"}), 400

        # Extract expense data
        expense_data = extract_receipt_data(receipt_text)

        return (
            jsonify({"expense": expense_data, "timestamp": datetime.now().isoformat()}),
            200,
        )

    except Exception as e:
        logging.error(f"Error extracting expense data: {str(e)}")
        return jsonify({"error": "Failed to extract expense data"}), 500


@ocr_bp.route("/extract-text", methods=["POST"])
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT["DEFAULT"])
def extract_text():
    """Extract text from receipt image without structured analysis."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]

        # File size validation
        if len(file.read()) > Config.OCR_MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400
        file.seek(0)  # Reset file pointer after reading

        # Save and process the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.OCR_UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Extract text using Google Vision
        with open(file_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if not response.text_annotations:
            return jsonify({"error": "No text detected in image"}), 400

        # Return extracted text
        extracted_text = response.text_annotations[0].description

        return (
            jsonify({"text": extracted_text, "timestamp": datetime.now().isoformat()}),
            200,
        )

    except Exception as e:
        logging.error(f"Error extracting text: {str(e)}")
        return jsonify({"error": "Failed to extract text"}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@ocr_bp.route("/process-batch", methods=["POST"])
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT["BATCH"])
async def process_receipt_batch():
    """Process multiple receipts in batch mode"""
    try:
        if "receipts" not in request.files:
            return jsonify({"error": "No receipt files provided"}), 400

        files = request.files.getlist("receipts")
        user_id = request.headers.get("X-User-ID")

        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        file_list = [{"filename": f.filename, "content": f.read()} for f in files]
        results = await ocr_controller.handle_batch_processing(file_list, user_id)

        return jsonify(results), 200

    except Exception as e:
        logging.error(f"Batch processing error: {str(e)}")
        return jsonify({"error": "Failed to process batch"}), 500


@ocr_bp.route("/batch-status/<batch_id>", methods=["GET"])
def get_batch_status(batch_id):
    """Get the status of a batch job"""
    status = batch_processor.get_batch_status(batch_id)
    return jsonify(status), 200
