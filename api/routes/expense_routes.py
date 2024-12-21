from flask import Blueprint, request, jsonify
from api.utils.db_utils import get_db_connection
import logging
from typing import Dict, Any, Optional
import os
import sqlite3
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv  # Added import for load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(
    filename="expense_routes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
    # Rule-based categorization
    if description:
        for keyword, category in CATEGORIES.items():
            if keyword.lower() in description.lower():
                return category

    # Fallback to AI-based categorization
    try:
        response = ai_client.completions.create(
            model="text-davinci-003",
            prompt=f"Categorize this expense description: '{description}' into categories: Food, Travel, Entertainment, Bills, General.",
            max_tokens=10
        )
        ai_category = response.choices[0].text.strip()
        return ai_category if ai_category else "General"
    except Exception as e:
        logging.warning(f"AI categorization failed: {e}")
        return "General"  # Always return "General" when categorization fails

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
    required_fields = ['user_id', 'description', 'amount']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
            
    if not isinstance(data.get('amount'), (int, float)) or data.get('amount') <= 0:
        return jsonify({"error": "Amount must be a positive number"}), 400

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

        # Categorize expense
        category = categorize_expense(description)

        cursor.execute(
            """
            INSERT INTO expenses (user_id, description, amount, category, date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, description, amount, category, date)
        )
        conn.commit()

        return jsonify({
            "message": "Expense added successfully",
            "description": description,
            "category": category,
            "date": date
        }), 201
    except Exception as e:
        logging.exception("Error adding expense")
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
