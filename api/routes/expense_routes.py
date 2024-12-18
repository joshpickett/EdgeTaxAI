from flask import Blueprint, request, jsonify
from db_utils import get_db_connection
from openai import OpenAI
import logging

# Configure Logging
logging.basicConfig(
    filename="expense_routes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Blueprint setup
expense_bp = Blueprint("expenses", __name__)

# Initialize AI (if needed for categorization)
AI_CLIENT = OpenAI(api_key="YOUR_OPENAI_KEY")

# Helper: Convert SQL row to dict
def row_to_dict(row):
    return {key: row[key] for key in row.keys()}

# Add Expense
@expense_bp.route("/add", methods=["POST"])
def add_expense():
    data = request.json
    user_id = data.get("user_id")
    description = data.get("description")
    amount = data.get("amount")

    if not all([user_id, description, amount]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Optional AI categorization
        category = AI_CLIENT.categorize(description) if description else "Uncategorized"

        cursor.execute(
            "INSERT INTO expenses (user_id, description, amount, category) VALUES (?, ?, ?, ?)",
            (user_id, description, amount, category)
        )
        conn.commit()

        return jsonify({"message": "Expense added successfully", "category": category}), 201
    except Exception as e:
        logging.exception("Error adding expense")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

# List Expenses
@expense_bp.route("/list/<int:user_id>", methods=["GET"])
def list_expenses(user_id):
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
    data = request.json
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")

    if not any([description, amount, category]):
        return jsonify({"error": "No data provided for update"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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

        if cursor.rowcount == 0:
            return jsonify({"error": "Expense not found"}), 404

        return jsonify({"message": "Expense updated successfully"}), 200
    except Exception as e:
        logging.exception("Error updating expense")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()

# Delete Expense
@expense_bp.route("/delete/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Expense not found"}), 404

        return jsonify({"message": "Expense deleted successfully"}), 200
    except Exception as e:
        logging.exception("Error deleting expense")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        conn.close()
