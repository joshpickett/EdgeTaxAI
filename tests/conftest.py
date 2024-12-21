import pytest
import sqlite3
import tempfile
import os
from datetime import datetime
from flask import Flask
from api.routes.expense_routes import expense_bp
from api.routes.auth_routes import auth_bp


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary database path and set it as the DATABASE environment variable."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test_database.db")
        os.environ["DATABASE"] = db_path  # Set the DATABASE environment variable
        print(f"Database initialized at: {db_path}")
        yield db_path  # Provide the database path to other fixtures


@pytest.fixture(scope="session", autouse=True)
def setup_database(test_db_path):
    """Initialize the test database schema (create tables)."""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()

    # Create 'users' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            phone_number TEXT UNIQUE,
            password TEXT NOT NULL,
            otp_code TEXT,
            otp_expiry TIMESTAMP,
            is_verified BOOLEAN DEFAULT 0
        )
    """)

    # Create 'expenses' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # Create 'reminders' table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reminder_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database schema created successfully.")


@pytest.fixture
def client(test_db_path):
    """Flask test client with a fresh database state for each test."""
    app = Flask(__name__)
    app.register_blueprint(expense_bp)
    app.register_blueprint(auth_bp)
    app.config["TESTING"] = True

    def reset_database():
        """Reset the database to a clean state with a sample user and expense."""
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM expenses")
        cursor.execute("DELETE FROM reminders")
        conn.commit()

        # Add a sample user
        cursor.execute(
            "INSERT INTO users (id, email, phone_number, password) VALUES (?, ?, ?, ?)",
            (1, "test@example.com", "+1234567890", "password123")
        )

        # Add a sample expense
        cursor.execute(
            "INSERT INTO expenses (id, user_id, description, amount, category, date) VALUES (?, ?, ?, ?, ?, ?)",
            (1, 1, "Sample Expense", 50.0, "General", datetime.now().strftime("%Y-%m-%d"))
        )

        conn.commit()
        conn.close()
        print("Database reset for test with sample data.")

    reset_database()

    # Provide the Flask test client
    with app.test_client() as client:
        yield client

import logging

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_setup(item):
    logging.info(f"Starting test: {item.name}")
    yield
    logging.info(f"Finished test: {item.name}")
