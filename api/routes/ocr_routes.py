import os
import sys
from api.setup_path import setup_python_path
setup_python_path(__file__)

from flask import Blueprint, request, jsonify
import logging
import time
from functools import wraps
from typing import Dict, Any, Optional, Tuple, List
from werkzeug.utils import secure_filename
import json
import hashlib
import re
from google.cloud import vision
from datetime import datetime
from api.utils.error_handler import handle_api_error
from api.utils.cache_utils import CacheManager, cache_response
from api.utils.ai_utils import extract_receipt_data, analyze_receipt_text
from api.utils.monitoring import monitor_api_calls
from api.utils.rate_limit import rate_limit
from api.config import Config
from api.utils.ocr_processor import OCRProcessor
from api.utils.ai_document_classifier import DocumentClassifier
from api.utils.document_manager import DocumentManager
from api.utils.income_service import IncomeService
from api.utils.expense_service import ExpenseService
from decimal import Decimal

# Create upload folder
os.makedirs(Config.OCR_UPLOAD_FOLDER, exist_ok=True)

# Configure Logging
logging.basicConfig(
    filename="ocr.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize components
ocr_bp = Blueprint("ocr", __name__)
ocr_processor = OCRProcessor()
document_classifier = DocumentClassifier()
document_manager = DocumentManager()
income_service = IncomeService()
expense_service = ExpenseService()

# Initialize session and token managers
session_manager = SessionManager()  # Initialize at module level
token_manager = TokenManager()  # Initialize at module level

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
            logging.info(f"Extracted {field}: {extracted_fields[field]}")

        return extracted_fields
    except Exception as e:
        logging.error(f"Text extraction failed: {e}")
        return None

@ocr_bp.route("/process-receipt", methods=["POST"])
@monitor_api_calls("process_receipt")
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT['DEFAULT'])
@cache_response(timeout=3600)  # Cache for 1 hour
def process_receipt():
    """Process receipt image and extract relevant information."""
    try:
        cache_manager = CacheManager()

        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        
        # File size validation
        if len(file.read()) > Config.OCR_MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400
        file.seek(0)  # Reset file pointer after reading

        if not allowed_file_extension(file.filename, Config.OCR_ALLOWED_EXTENSIONS):
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
        file_path = os.path.join(Config.OCR_UPLOAD_FOLDER, filename)
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

        # Classify document
        doc_type, confidence, metadata = document_classifier.classify_document(
            extracted_text
        )
        
        # Extract financial data
        financial_data = document_classifier.extract_financial_data(
            extracted_text,
            doc_type
        )
        
        # Combine all metadata
        combined_metadata = {
            **metadata,
            **financial_data
        }
        
        user_id = request.headers.get('X-User-ID')
        
        # Determine if document is income or expense related
        if document_classifier.should_store_as_income(doc_type, combined_metadata):
            # Create income record
            income_data = {
                'user_id': user_id,
                'gross_income': Decimal(str(financial_data.get('total_amount', 0))),
                'payer_name': financial_data.get('payer_name', ''),
                'date': financial_data.get('date'),
                'document_id': None  # Will be updated after document storage
            }
            income_record = income_service.create_income(income_data)
            
        elif document_classifier.should_store_as_expense(doc_type, combined_metadata):
            # Create expense record
            expense_data = {
                'user_id': user_id,
                'amount': Decimal(str(financial_data.get('total_amount', 0))),
                'description': financial_data.get('description', ''),
                'date': financial_data.get('date'),
                'category': financial_data.get('category', 'OTHER'),
                'document_id': None  # Will be updated after document storage
            }
            expense_record = expense_service.create_expense(expense_data)

        # Store document with classification
        doc_result = document_manager.store_document({
            'user_id': user_id,
            'type': doc_type,
            'content': file_content,
            'filename': filename,
            'metadata': combined_metadata
        })

        # Update income/expense record with document ID
        if 'income_record' in locals():
            income_service.update_income(income_record.id, {'document_id': doc_result['document_id']})
        elif 'expense_record' in locals():
            expense_service.update_expense(expense_record.id, {'document_id': doc_result['document_id']})

        return jsonify({
            'status': 'success',
            'document_id': doc_result['document_id'],
            'document_type': doc_type,
            'confidence_score': confidence,
            'extracted_data': combined_metadata
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process receipt: {str(e)}"}), 500

@ocr_bp.route("/analyze-receipt", methods=["POST"])
@monitor_api_calls("analyze_receipt")
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT['DEFAULT'])
@cache_response(timeout=1800)  # Cache for 30 minutes
def analyze_receipt():
    """Analyze receipt image and extract structured data."""
    try:
        if "receipt" not in request.files:
            return jsonify({"error": "No receipt file provided"}), 400

        file = request.files["receipt"]
        
        # File size validation
        if len(file.read()) > Config.OCR_MAX_FILE_SIZE:
            return jsonify({"error": "File size exceeds 10MB limit"}), 400
        file.seek(0)  # Reset file pointer after reading

        if not allowed_file_extension(file.filename, Config.OCR_ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

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
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT['DEFAULT'])
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
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT['DEFAULT'])
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

        if not allowed_file_extension(file.filename, Config.OCR_ALLOWED_EXTENSIONS):
            return jsonify({"error": "Invalid file type"}), 400

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
@rate_limit(requests_per_minute=Config.OCR_RATE_LIMIT['BATCH'])
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

def extract_vendor_field(text: str) -> Optional[str]:
    """Extract vendor name from receipt text using pattern matching and AI."""
    try:
        # Common business identifiers
        business_patterns = [
            r'^([A-Z\s&]+)\n',  # Business name at start of receipt
            r'((?:Inc|LLC|Ltd|Corp|Corporation|Company)[\.:\s]+[A-Za-z\s&]+)',
            r'(?:Store|Restaurant|Cafe):\s*([A-Za-z0-9\s&]+)'
        ]
        
        for pattern in business_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # If patterns fail, use first non-empty line
        first_line = next((line.strip() for line in text.split('\n') 
                         if line.strip()), None)
        return first_line
    except Exception as e:
        logging.error(f"Vendor extraction failed: {e}")
        return None

def extract_line_items(text: str) -> List[Dict[str, Any]]:
    """Extract individual line items from receipt text."""
    try:
        items = []
        lines = text.split('\n')
        item_pattern = r'([A-Za-z0-9\s&\-\'\"]+)\s+(\d+(?:\.\d{2})?)'
        
        for line in lines:
            # Skip total lines
            if re.search(r'total|subtotal|tax|amount due', line, re.IGNORECASE):
                continue
                
            match = re.search(item_pattern, line)
            if match:
                description = match.group(1).strip()
                price = float(match.group(2))
                items.append({
                    'description': description,
                    'price': price
                })
        
        return items
    except Exception as e:
        logging.error(f"Line item extraction failed: {e}")
        return []
