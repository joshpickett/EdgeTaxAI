from flask import Blueprint, request, jsonify
from utils.db_utils import get_db_connection
from utils.ai_utils import categorize_expense
import sqlite3
import logging

# Configure Logging
logging.basicConfig(
    filename="expense_routes.log",  # Log file for expense routes
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint setup
expense_bp = Blueprint("expenses", __name__)

@expense_bp.route("/add", methods=["POST"])
def add_expense():
    """
    Add Expense Endpoint: Adds a new expense with AI-based categorization.
    """
    data = request.json
    user_id = data.get("user_id")
    description = data.get("description")
    amount = data.get("amount")

    # Input Validation
    if not all([user_id, description, amount]):
        logging.warning("Failed expense addition: Missing required fields.")
        return jsonify({"error": "Missing required fields: user_id, description, and amount."}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            logging.warning(f"Failed expense addition: Invalid amount ({amount}) for user {user_id}.")
            return jsonify({"error": "Amount must be a positive number."}), 400
    except ValueError:
        logging.warning(f"Failed expense addition: Invalid amount format ({amount}) for user {user_id}.")
        return jsonify({"error": "Amount must be a valid numeric value."}), 400

    # Categorize Expense using AI
    try:
        category = categorize_expense(description)
        logging.info(f"AI Categorization: '{description}' categorized as '{category}'.")

        conn = get_db_connection()
        if conn is None:
            logging.error("Database connection failed during expense addition.")
            return jsonify({"error": "Internal server error. Please try again later."}), 500

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, description, amount, category) VALUES (?, ?, ?, ?)",
            (user_id, description, amount, category)
        )
        conn.commit()
        logging.info(f"Expense '{description}' added successfully for user {user_id}.")

        return jsonify({"message": "Expense added successfully.", "category": category}), 200
    except sqlite3.Error as e:
        logging.error(f"Database error during expense addition for user {user_id}: {e}")
        return jsonify({"error": "Failed to add expense. Please try again later."}), 500
    except Exception as e:
        logging.exception(f"Unexpected error during expense addition for user {user_id}: {e}")
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
    finally:
        if conn:
            conn.close()


@expense_bp.route("/list/<int:user_id>", methods=["GET"])
def list_expenses(user_id):
    """
    List Expenses Endpoint: Fetches all expenses for a specific user.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            logging.error("Database connection failed during expense retrieval.")
            return jsonify({"error": "Internal server error. Please try again later."}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
        expenses = cursor.fetchall()

        if not expenses:
            logging.info(f"No expenses found for user {user_id}.")
            return jsonify({"expenses": [], "message": "No expenses found."}), 200

       
