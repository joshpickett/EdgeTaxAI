from flask import Blueprint, request, jsonify
from api.utils.db_utils import get_db_connection
import logging
from typing import Dict, Any, Optional
import os
import sqlite3
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from ..utils.ai_utils import categorize_expense, analyze_expense_pattern
from ..utils.tax_calculator import TaxCalculator
from ..routes.tax_routes import calculate_tax_implications
from ..routes.irs_routes import verify_irs_compliance
from ..routes.ocr_routes import process_receipt_data
from ..routes.ocr_routes import extract_receipt_data, analyze_receipt_text
from ..routes.reports_routes import update_expense_reports

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(
    filename="expense_routes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Input validation constants
MAX_DESCRIPTION_LENGTH = 500
MIN_AMOUNT = 0.01
MAX_AMOUNT = 1000000.00
ALLOWED_CATEGORIES = [
    'Food', 'Travel', 'Entertainment', 
    'Office Supplies', 'Vehicle', 
    'Insurance', 'Utilities', 'Other'
]

class ExpenseValidationError(Exception):
    pass

# Blueprint setup
expense_bp = Blueprint("expenses", __name__)

# OpenAI setup
openai_api_key = os.getenv("OPENAI_API_KEY", "dummy_key")
ai_client = OpenAI(api_key=openai_api_key)

# Load categories.json
CATEGORIES_FILE = os.path.join(os.path.dirname(__file__), "../utils/categories.json")
try:
    with open(CATEGORIES_FILE, "r") as f:
        CATEGORIES = json.load(f)
except FileNotFoundError:
    CATEGORIES = {}
    logging.warning("categories.json not found. Rule-based categorization will be skipped.")

# Categorize Expense Function
def categorize_expense(description):
    """Categorize expense based on description using rule-based and AI-based logic."""
    # First check learning system for previous categorizations
    learned_categories = get_learned_categories(description)
    if learned_categories:
        best_match = max(learned_categories, key=lambda x: x['confidence'])
        if best_match['confidence'] > 0.8:
            return {
                'category': best_match['category'],
                'confidence': best_match['confidence'],
                'source': 'learning_system'
            }

    # Fallback to AI-based categorization
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """Analyze this expense and provide:
                    1. Category (Travel, Meals, Office Supplies, Vehicle, Entertainment, Other)
                    2. Confidence score (0-1)
                    3. Reasoning for categorization
                    Format: category|confidence|reasoning"""
            }, {
                "role": "user",
                "content": f"Categorize this expense: {description}"
            }]
        )
        result = response.choices[0].message.content.strip().split("|")
        return {
            'category': result[0].strip(),
            'confidence': float(result[1]),
            'reasoning': result[2].strip(),
            'source': 'ai'
        }
    except Exception as e:
        logging.warning(f"AI categorization failed: {e}")
        return {"category": "General", "confidence": 0, "reasoning": "AI failed", "source": "ai"}  # Always return "General" when categorization fails

# Helper: Convert SQL row to dict
def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

# Add Expense
@expense_bp.route("/add", methods=["POST"])
def add_expense() -> tuple[Dict[str, Any], int]:
    """
    Adds a new expense.
    If description is not provided or empty, it defaults to 'Unspecified'.
    If date is not provided, it defaults to the current date.
    """
    data = request.json
    
    # Enhanced input validation
    if not data:
        return jsonify({"error": "No data provided"}), 400
            
    # Enhanced input validation
    try:
        description = data.get("description")
        amount = data.get("amount")
        category = data.get("category")

        # Validate description
        if not description or len(description) > MAX_DESCRIPTION_LENGTH:
            raise ExpenseValidationError(
                f"Description must be between 1 and {MAX_DESCRIPTION_LENGTH} characters"
            )

        # Validate amount
        if not isinstance(amount, (int, float)) or amount < MIN_AMOUNT or amount > MAX_AMOUNT:
            raise ExpenseValidationError(
                f"Amount must be between {MIN_AMOUNT} and {MAX_AMOUNT}"
            )

        # Validate category if provided
        if category and category not in ALLOWED_CATEGORIES:
            raise ExpenseValidationError(
                f"Invalid category. Must be one of: {', '.join(ALLOWED_CATEGORIES)}"
            )

    except ExpenseValidationError as e:
        return jsonify({"error": str(e)}), 400

    user_id = data.get("user_id")
    description = data.get("description", "").strip() or "General"
    amount = data.get("amount")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    # Input Validation
    if not isinstance(user_id, int) or user_id <= 0:
        return jsonify({"error": "Invalid user ID"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Enhanced tax context analysis
        tax_context = analyze_tax_context(description, amount)
        
        # Get tax implications
        tax_implications = calculate_tax_implications(amount, category)
        irs_status = verify_irs_compliance(description, amount, category)
        
        # Get recent expenses for pattern analysis
        cursor.execute(
            "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 50",
            (user_id,)
        )
        recent_expenses = cursor.fetchall()
        patterns = analyze_expense_pattern(recent_expenses)
        
        # Enhanced AI categorization with pattern matching
        ai_category = categorize_expense(description)
        pattern_category = get_pattern_based_category(description, amount, patterns)
        
        # Combine AI and pattern-based categorization
        final_category = combine_categorizations(ai_category, pattern_category)
         
        # Log categorization results
        logging.info(f"Expense categorized as {final_category['category']} with confidence {final_category['confidence']}")
        
        # Store with confidence score
        cursor.execute(
            """INSERT INTO expenses 
               (user_id, description, amount, category,
                tax_context, irs_category, deductible_amount,
                compliance_score, tax_implications, irs_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, description, amount, final_category['category'],
             tax_context['context'], tax_context['suggested_category'],
             tax_context['deductible_amount'], irs_status['compliance_score'], tax_implications, irs_status)
        )
        conn.commit()

        # Update reports
        update_expense_reports(user_id)
        
        return jsonify({
            "message": "Expense added successfully",
            "description": description,
            "category": final_category['category'],
            "date": date
        }), 201
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")
        logging.error(f"Database error: {e}")
        return jsonify({"error": "Database operation failed"}), 500
    except Exception as e:
        if 'cursor' in locals():
            cursor.execute("ROLLBACK")
        logging.exception(f"Error adding expense: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

# List Expenses
@expense_bp.route("/list/<int:user_id>", methods=["GET"])
def list_expenses(user_id):
    """Lists all expenses for a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row

        cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
        expenses = cursor.fetchall()

        return jsonify([row_to_dict(row) for row in expenses]), 200
    except Exception as e:
        logging.exception("Error listing expenses")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

# Edit Expense
@expense_bp.route("/edit/<int:expense_id>", methods=["PUT"])
def edit_expense(expense_id):
    """Edits an existing expense."""
    data = request.json
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")

    if not any([description, amount, category]):
        return jsonify({"error": "No data provided for update"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the expense exists
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Expense not found"}), 404

        # Prepare update query
        updates = []
        params = []

        if description:
            updates.append("description = ?")
            params.append(description)
        if amount:
            updates.append("amount = ?")
            params.append(amount)
        if category:
            updates.append("category = ?")
            params.append(category)

        params.append(expense_id)
        update_query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"

        cursor.execute(update_query, params)
        conn.commit()

        return jsonify({"message": "Expense updated successfully"}), 200
    except Exception as e:
        logging.exception("Error updating expense")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

# Delete Expense
@expense_bp.route("/delete/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    """Deletes an expense by ID."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the expense exists
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Expense not found"}), 404

        # Delete the expense
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        logging.exception("Error deleting expense")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()
