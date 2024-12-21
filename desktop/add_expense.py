import sqlite3
from db_utils import get_db_connection
import logging
from typing import Optional, Dict, Any
import requests
from werkzeug.utils import secure_filename
import os

# Configure Logging
logging.basicConfig(
    filename="add_expense.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# API Configuration
API_BASE_URL = "http://localhost:5000/api"
OCR_API_URL = f"{API_BASE_URL}/process-receipt"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_receipt_ocr(file_path) -> Optional[Dict[str, Any]]:
    """Send the receipt image to the OCR API for text extraction."""
    try:
        with open(file_path, "rb") as file:
            files = {"receipt": file}
            headers = {"X-User-ID": str(st.session_state.get("user_id", ""))}
            response = requests.post(OCR_API_URL, files=files, headers=headers)
            
        if response.status_code == 200:
            data = response.json()
            return {
                "text": data.get("text", ""),
                "expense_id": data.get("expense_id"),
                "document_id": data.get("document_id")
            }
        else:
            logging.error(f"OCR API Error: {response.json().get('error', 'Unknown error')}")
            return None
    except Exception as e:
        logging.exception(f"Error during OCR processing: {e}")
        return None

def add_expense():
    """Add a new expense to the database."""
    description = input("Enter expense description: ").strip()
    amount = input("Enter expense amount: ").strip()
    category = input("Enter expense category (e.g., Food, Transport): ").strip()
    receipt_path = input("Enter receipt file path (optional): ").strip()

    # OCR Processing for Receipts
    if receipt_path:
        try:
            filename = secure_filename(os.path.basename(receipt_path))
            saved_file_path = os.path.join(UPLOAD_FOLDER, filename)
            os.rename(receipt_path, saved_file_path)
            print("Processing receipt for text extraction...")
            ocr_result = process_receipt_ocr(saved_file_path)
            if ocr_result and ocr_result.get("text"):
                print("Extracted Text from Receipt:")
                print(ocr_result["text"])
                # Suggest description based on OCR result
                description = description or ocr_result["text"].split("\n")[0]  # Use first line as suggestion
        except Exception as e:
            logging.exception(f"Error saving receipt file: {e}")
            print("Error: Could not save or process the receipt.")

    if not description or not amount:
        print("Error: Description and amount are required fields.")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            print("Error: Amount must be a positive number.")
            return
    except ValueError:
        print("Error: Invalid amount format.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create expense entry via API
        expense_payload = {
            "description": description,
            "amount": amount,
            "category": category
        }
        
        response = requests.post(f"{API_BASE_URL}/expenses", json=expense_payload)
        if response.status_code != 201:
            raise Exception("Failed to create expense via API")
            
        print("Expense added successfully!")
        logging.info(f"Expense added: {description} - ${amount} - {category}")
    except Exception as e:
        logging.exception(f"Error adding expense: {e}")
        print("Error: Could not add the expense.")
    finally:
        conn.close()

def edit_expense():
    """Edit an existing expense."""
    try:
        expense_id = input("Enter the ID of the expense to edit: ").strip()
        if not expense_id.isdigit():
            print("Error: Invalid expense ID.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        expense = cursor.fetchone()

        if not expense:
            print(f"Error: No expense found with ID {expense_id}.")
            return

        print("Leave a field blank to keep its current value.")
        description = input(f"Enter new description (current: {expense['description']}): ").strip()
        amount = input(f"Enter new amount (current: ${expense['amount']}): ").strip()
        category = input(f"Enter new category (current: {expense['category']}): ").strip()

        updates = []
        params = []

        if description:
            updates.append("description = ?")
            params.append(description)
        if amount:
            try:
                amount = float(amount)
                updates.append("amount = ?")
                params.append(amount)
            except ValueError:
                print("Error: Invalid amount format.")
                return
        if category:
            updates.append("category = ?")
            params.append(category)

        if not updates:
            print("No updates made.")
            return

        params.append(expense_id)
        update_query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(update_query, params)
        conn.commit()

        print("Expense updated successfully!")
        logging.info(f"Expense {expense_id} updated successfully.")
    except Exception as e:
        logging.exception(f"Error editing expense: {e}")
        print("Error: Could not edit the expense.")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Expense Management")
    print("1. Add Expense")
    print("2. Edit Expense")
    option = input("Choose an option (1 or 2): ").strip()

    if option == "1":
        add_expense()
    elif option == "2":
        edit_expense()
    else:
        print("Invalid option. Please choose 1 or 2.")
