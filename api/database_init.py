import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("taxedgeai.db")
c = conn.cursor()

# Create 'users' table
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT UNIQUE,
    password TEXT NOT NULL,
    otp_code TEXT,
    otp_expiry TIMESTAMP,
    is_verified BOOLEAN DEFAULT 0,  -- 0 = Not verified, 1 = Verified
    tax_strategy TEXT DEFAULT 'Mileage'  -- Options: 'Mileage' or 'Actual'
)
""")

# Create 'expenses' table (Recreate if needed)
c.execute("PRAGMA foreign_keys=off;")  # Disable foreign keys temporarily
c.execute("DROP TABLE IF EXISTS expenses;")  # Drop the old table

c.execute("""
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT DEFAULT 'Uncategorized',
    confidence_score REAL DEFAULT 0.0,
    tax_context TEXT DEFAULT 'personal',
    learning_feedback TEXT,
    date TEXT NOT NULL,
    receipt TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")
c.execute("PRAGMA foreign_keys=on;")  # Re-enable foreign keys

# Create 'mileage' table
c.execute("""
CREATE TABLE IF NOT EXISTS mileage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_location TEXT NOT NULL,
    end_location TEXT NOT NULL,
    distance REAL NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

# Create 'reminders' table
c.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    phone_number TEXT NOT NULL,
    reminder_date TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

# Create 'bank_accounts' table
c.execute("""
CREATE TABLE IF NOT EXISTS bank_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    bank_name TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

# Create 'bank_transactions' table
c.execute("""
CREATE TABLE IF NOT EXISTS bank_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

# Create 'category_learning' table
c.execute("""
CREATE TABLE IF NOT EXISTS category_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_category TEXT NOT NULL,
    corrected_category TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
""")

# Create 'category_patterns' table
c.execute("""
CREATE TABLE IF NOT EXISTS category_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL DEFAULT 0.0
)
""")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database schema updated successfully!")
