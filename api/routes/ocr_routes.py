from flask import Blueprint, request, jsonify
import logging
import os
from google.cloud import vision
from werkzeug.utils import secure_filename
from datetime import datetime
from ..utils.error_handler import handle_api_error
from ..utils.ai_utils import extract_receipt_data, analyze_receipt_text

# Configure Logging
logging.basicConfig(
    filename="ocr.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint setup
ocr_bp = Blueprint("ocr", __name__)

# Initialize Google Cloud Vision client
try:
    client = vision.ImageAnnotatorClient()
except Exception as e:
    logging.error(f"Failed to initialize Google Cloud Vision client: {e}")
    client = None

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file_extension(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@ocr_bp.route("/process-receipt", methods=["POST"])
def process_receipt():
    """Process receipt image and extract relevant information."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        if not allowed_file_extension(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Load image into Google Vision
        with open(file_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            return jsonify({"error": "No text detected in the image"}), 400

        # Extract detected text
        extracted_text = texts[0].description

        # Return the extracted text
        return jsonify({"text": extracted_text}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process receipt: {str(e)}"}), 500

@ocr_bp.route("/analyze-receipt", methods=["POST"])
def analyze_receipt():
    """Analyze receipt image and extract structured data."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        if not allowed_file_extension(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

        # Save and process the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # Extract text using Google Vision
        with open(file_path, "rb") as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        
        if not response.text_annotations:
            return jsonify({"error": "No text detected in image"}), 400

        # Extract structured data
        extracted_data = extract_receipt_data(response.text_annotations[0].description)
        
        return jsonify({
            "data": extracted_data,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logging.error(f"Error analyzing receipt: {str(e)}")
        return jsonify({"error": "Failed to analyze receipt"}), 500
    finally:
        # Cleanup: Remove uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@ocr_bp.route("/extract-expense", methods=["POST"])
def extract_expense():
    """Extract expense information from receipt text."""
    try:
        data = request.json
        receipt_text = data.get("text")

        if not receipt_text:
            return jsonify({"error": "Receipt text is required"}), 400

        # Extract expense data
        expense_data = extract_receipt_data(receipt_text)

        return jsonify({
            "expense": expense_data,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logging.error(f"Error extracting expense data: {str(e)}")
        return jsonify({"error": "Failed to extract expense data"}), 500

@ocr_bp.route("/extract-text", methods=["POST"])
def extract_text():
    """Extract text from receipt image without structured analysis."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        if not allowed_file_extension(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

        # Save and process the file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
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
        
        return jsonify({
            "text": extracted_text,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logging.error(f"Error extracting text: {str(e)}")
        return jsonify({"error": "Failed to extract text"}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
