import sqlite3
import logging

# Configure Logging
logging.basicConfig(
    filename="db_utils.log",  # Log file for database issues
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DATABASE_FILE = "database.db"

def get_db_connection():
    """
    Establishes a connection to the SQLite database with error handling.

    Returns:
        Connection object if successful, None otherwise.
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        logging.info("Database connection established successfully.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None


def save_user(full_name, email, phone_number, password):
    """
    Saves a new user to the database.

    Args:
        full_name (str): User's full name.
        email (str): User's email address.
        phone_number (str): User's phone number.
        password (str): Hashed password.

    Returns:
        True if successful, False otherwise.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to save user: Database connection could not be established.")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (full_name, email, phone_number, password) VALUES (?, ?, ?, ?)",
            (full_name, email, phone_number, password)
        )
        conn.commit()
        logging.info(f"User {email} saved successfully.")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error saving user {email}: {e}")
        return False
    finally:
        conn.close()


def fetch_user_by_email(email):
    """
    Fetches a user from the database using their email.

    Args:
        email (str): User's email address.

    Returns:
        Dictionary containing user data if found, None otherwise.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to fetch user: Database connection could not be established.")
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
            logging.info(f"User {email} fetched successfully.")
            return dict(user)
        else:
            logging.warning(f"No user found with email: {email}")
            return None
    except sqlite3.Error as e:
        logging.error(f"Error fetching user {email}: {e}")
        return None
    finally:
        conn.close()


def save_expense(user_id, description, amount, category):
    """
    Saves an expense to the database.

    Args:
        user_id (int): ID of the user.
        description (str): Expense description.
        amount (float): Expense amount.
        category (str): Expense category.

    Returns:
        True if successful, False otherwise.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to save expense: Database connection could not be established.")
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, description, amount, category) VALUES (?, ?, ?, ?)",
            (user_id, description, amount, category)
        )
        conn.commit()
        logging.info(f"Expense '{description}' for user {user_id} saved successfully.")
        return True
    except sqlite3.Error as e:
        logging.error(f"Error saving expense '{description}' for user {user_id}: {e}")
        return False
    finally:
        conn.close()


def fetch_expenses_by_user(user_id):
    """
    Fetches all expenses for a given user.

    Args:
        user_id (int): ID of the user.

    Returns:
        List of expense records if successful, empty list otherwise.
    """
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to fetch expenses: Database connection could not be established.")
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
        expenses = cursor.fetchall()
        logging.info(f"Fetched {len(expenses)} expenses for user {user_id}.")
        return [dict(row) for row in expenses]
    except sqlite3.Error as e:
        logging.error(f"Error fetching expenses for user {user_id}: {e}")
        return []
    finally:
        conn.close()
