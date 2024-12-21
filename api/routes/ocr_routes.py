from flask import Blueprint, request, jsonify
import os
from google.cloud import vision
from werkzeug.utils import secure_filename

# Blueprint setup
ocr_bp = Blueprint("ocr", __name__)

# Set up Google Vision Client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your-service-account.json"
client = vision.ImageAnnotatorClient()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@ocr_bp.route("/ocr/receipt", methods=["POST"])
def process_receipt():
    """
    Process a receipt image using Google Vision API and extract text.
    """
    if "receipt" not in request.files:
        return jsonify({"error": "No receipt file provided"}), 400

    file = request.files["receipt"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
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
