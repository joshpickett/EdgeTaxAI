from flask import Blueprint, request, jsonify
import logging
import time
from functools import wraps
from typing import Dict, Any, Optional, Tuple
from werkzeug.utils import secure_filename
import os
import redis
import json
import hashlib
import re
from google.cloud import vision
from datetime import datetime
from ..utils.error_handler import handle_api_error
from ..utils.cache_utils import CacheManager, cache_response
from ..utils.ai_utils import extract_receipt_data, analyze_receipt_text
from ..utils.monitoring import monitor_api_calls
from ..utils.batch_processor import BatchProcessor
from ..utils.expense_integration import ExpenseIntegration
from ..utils.document_manager import DocumentManager

# Configure Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Constants for validation
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour

# Create upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Logging
logging.basicConfig(
    filename="ocr.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize components
ocr_bp = Blueprint("ocr", __name__)
batch_processor = BatchProcessor()
document_manager = DocumentManager()
expense_integration = ExpenseIntegration()

# Initialize Google Cloud Vision client
try:
    client = vision.ImageAnnotatorClient()
except Exception as e:
    logging.error(f"Failed to initialize Google Cloud Vision client: {e}")
    client = None

def allowed_file_extension(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_cache_key(file_content: bytes) -> str:
    """Generate a cache key from file content."""
    return hashlib.md5(file_content).hexdigest()

# Performance monitoring decorator
def monitor_performance(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Function {f.__name__} took {end_time - start_time:.2f} seconds")
        return result
    return wrapper

def extract_text_from_image(image):
    """Extract text from image with enhanced field detection."""
    try:
        # Initialize field extractors
        field_extractors = {
            'date': extract_date_field,
            'total': extract_total_field,
            'vendor': extract_vendor_field,
            'items': extract_line_items
        }
        
        # Extract all fields
        extracted_fields = {}
        for field, extractor in field_extractors.items():
            extracted_fields[field] = extractor(image)

        return extracted_fields
    except Exception as e:
        logging.error(f"Text extraction failed: {e}")
        return None

@ocr_bp.route("/process-receipt", methods=["POST"])
@monitor_api_calls("process_receipt")
@cache_response(timeout=3600)  # Cache for 1 hour
def process_receipt():
    """Process receipt image and extract relevant information."""
    try:
        cache_manager = CacheManager()
         
        # Rate limiting check
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({"error": "User ID required in headers"}), 401

        rate_key = f"rate_limit:{user_id}"
        request_count = redis_client.get(rate_key)
        
        if request_count and int(request_count) >= RATE_LIMIT_REQUESTS:
            return jsonify({"error": "Rate limit exceeded"}), 429

        redis_client.incr(rate_key)
        redis_client.expire(rate_key, RATE_LIMIT_WINDOW)

        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        
        # File size validation
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400
        file.seek(0)  # Reset file pointer after reading

        if not allowed_file_extension(file.filename, ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

        if not file.filename:
            return jsonify({"error": "No selected file"}), 400

        # Check cache using CacheManager
        file_content = file.read()
        file.seek(0)
        cache_key = get_cache_key(file_content)
        
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            logging.info(f"Cache hit for key: {cache_key}")
            return jsonify(cached_result), 200

        logging.info(f"Cache miss for key: {cache_key}")

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

        # Cache the result
        try:
            result = {"text": extracted_text}
            cache_manager.set(cache_key, result, 3600)  # Cache for 1 hour
            logging.info(f"Cached result for key: {cache_key}")
        except Exception as e:
            logging.error(f"Cache storage error: {e}")

        # Create expense entry
        expense_id = expense_integration.create_expense_entry({
            'description': extracted_text,
            'amount': None,  # Placeholder for amount extraction
            'category': None,  # Placeholder for category extraction
            'date': None,  # Placeholder for date extraction
            'receipt_url': file_path,
            'confidence_score': None  # Placeholder for confidence score extraction
        }, user_id)

        # Store document
        doc_result = document_manager.store_document({
            'user_id': user_id,
            'type': 'receipt',
            'content': file_content,
            'metadata': {
                'description': extracted_text,
                'expense_id': expense_id
            }
        })

        # Return the extracted text
        return jsonify({
            "text": extracted_text,
            "expense_id": expense_id,
            "document_id": doc_result.get('document_id')
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process receipt: {str(e)}"}), 500

@ocr_bp.route("/analyze-receipt", methods=["POST"])
@monitor_api_calls("analyze_receipt")
@cache_response(timeout=1800)  # Cache for 30 minutes
def analyze_receipt():
    """Analyze receipt image and extract structured data."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        
        # File size validation
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400
        file.seek(0)  # Reset file pointer after reading

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
        
        # File size validation
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400
        file.seek(0)  # Reset file pointer after reading

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

@ocr_bp.route("/process-batch", methods=["POST"])
async def process_receipt_batch():
    """Process multiple receipts in batch mode"""
    try:
        if "receipts" not in request.files:
            return jsonify({"error": "No receipt files provided"}), 400

        files = request.files.getlist("receipts")
        user_id = request.headers.get('X-User-ID')

        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        # Prepare files for batch processing
        file_list = []
        for file in files:
            if file and allowed_file_extension(file.filename):
                file_data = {
                    'filename': file.filename,
                    'content': file.read()
                }
                file_list.append(file_data)

        # Start batch processing
        batch_id = await batch_processor.process_batch(file_list, user_id)

        return jsonify({
            "batch_id": batch_id,
            "message": "Batch processing started",
            "status_endpoint": f"/api/batch-status/{batch_id}"
        }), 202

    except Exception as e:
        logging.error(f"Batch processing error: {str(e)}")
        return jsonify({"error": "Failed to process batch"}), 500

@ocr_bp.route("/batch-status/<batch_id>", methods=["GET"])
def get_batch_status(batch_id):
    """Get the status of a batch job"""
    status = batch_processor.get_batch_status(batch_id)
    return jsonify(status), 200

def extract_date_field(text):
    """Extract date from receipt text using regex and AI."""
    try:
        # Common date patterns
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}',
            r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group()

        # AI-based date extraction if regex fails
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "Extract the date from this receipt text. Return in YYYY-MM-DD format."
            }, {
                "role": "user",
                "content": text
            }]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Date extraction failed: {e}")
        return None

def extract_total_field(text):
    """Extract total amount from receipt text."""
    try:
        # Common total amount patterns
        total_patterns = [
            r'TOTAL[\s:]*\$?\s*(\d+\.\d{2})',
            r'Amount[\s:]*\$?\s*(\d+\.\d{2})',
            r'Due[\s:]*\$?\s*(\d+\.\d{2})'
        ]

        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))

        # AI-based total extraction
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "Extract the total amount from this receipt text. Return only the number."
            }, {
                "role": "user",
                "content": text
            }]
        )
        return float(response.choices[0].message.content.strip())
    except Exception as e:
        logging.error(f"Total extraction failed: {e}")
        return None
