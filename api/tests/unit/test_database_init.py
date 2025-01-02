import pytest
import sqlite3
import os
from api.database_init import initialize_database


@pytest.fixture
def test_database_path():
    """Fixture for test database path"""
    database_path = "test_taxedgeai.db"
    yield database_path
    if os.path.exists(database_path):
        os.remove(database_path)


def test_database_initialization(test_database_path):
    """Test database initialization"""
    # Initialize test database
    initialize_database(test_database_path)

    # Connect and verify tables
    connection = sqlite3.connect(test_database_path)
    cursor = connection.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}

    # Verify required tables exist
    required_tables = {
        "users",
        "expenses",
        "mileage",
        "reminders",
        "bank_accounts",
        "bank_transactions",
        "category_learning",
        "category_patterns",
    }

    assert required_tables.issubset(tables)

    # Close connection
    connection.close()


def test_table_schemas(test_database_path):
    """Test table schemas are correct"""
    initialize_database(test_database_path)
    connection = sqlite3.connect(test_database_path)
    cursor = connection.cursor()

    # Test users table schema
    cursor.execute("PRAGMA table_info(users);")
    user_columns = {row[1] for row in cursor.fetchall()}
    assert {
        "id",
        "full_name",
        "email",
        "phone_number",
        "password",
        "otp_code",
        "otp_expiry",
        "is_verified",
        "tax_strategy",
    }.issubset(user_columns)

    # Test expenses table schema
    cursor.execute("PRAGMA table_info(expenses);")
    expense_columns = {row[1] for row in cursor.fetchall()}
    assert {
        "id",
        "user_id",
        "description",
        "amount",
        "category",
        "confidence_score",
        "tax_context",
        "learning_feedback",
        "date",
        "receipt",
    }.issubset(expense_columns)

    connection.close()


def test_foreign_key_constraints(test_database_path):
    """Test foreign key constraints"""
    initialize_database(test_database_path)
    connection = sqlite3.connect(test_database_path)
    cursor = connection.cursor()

    # Verify foreign keys are enabled
    cursor.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1

    # Test foreign key constraints
    tables_with_foreign_key = [
        "expenses",
        "mileage",
        "reminders",
        "bank_accounts",
        "bank_transactions",
    ]

    for table in tables_with_foreign_key:
        cursor.execute(f"PRAGMA foreign_key_list({table});")
        foreign_keys = cursor.fetchall()
        assert len(foreign_keys) > 0
        assert any(
            foreign_key[2] == "users" for foreign_key in foreign_keys
        )  # References users table

    connection.close()


def test_default_values(test_database_path):
    """Test default values in tables"""
    initialize_database(test_database_path)
    connection = sqlite3.connect(test_database_path)
    cursor = connection.cursor()

    # Test user default values
    cursor.execute(
        """
        INSERT INTO users (full_name, email, phone_number, password)
        VALUES (?, ?, ?, ?)
    """,
        ("Test User", "test@example.com", "+1234567890", "password123"),
    )

    cursor.execute(
        "SELECT is_verified, tax_strategy FROM users WHERE email=?",
        ("test@example.com",),
    )
    row = cursor.fetchone()
    assert row[0] == 0  # is_verified default
    assert row[1] == "Mileage"  # tax_strategy default

    connection.close()
