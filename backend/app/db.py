"""
Database module for FinTrust Gateway
Fixed version with proper SQLite setup
"""
import sqlite3
import os
from datetime import datetime

# Use local database path
DB_PATH = "./fintrust.db"

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with all required tables and sample data"""
    print("📊 Initializing database...")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                account_id INTEGER,
                amount REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                merchant TEXT,
                description TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (account_id) REFERENCES user_accounts (id)
            )
        """)

        # Create audit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                encrypted INTEGER DEFAULT 0
            )
        """)

        # Check if we need to insert sample data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            print("📝 Inserting sample data...")

            # Insert sample users
            now = datetime.utcnow().isoformat()
            sample_users = [
                ("user-001", "john_doe", "john@example.com", now),
                ("user-002", "jane_smith", "jane@example.com", now),
                ("user-003", "bob_wilson", "bob@example.com", now)
            ]
            cursor.executemany(
                "INSERT INTO users (id, username, email, created_at) VALUES (?, ?, ?, ?)",
                sample_users
            )

            # Insert sample accounts
            sample_accounts = [
                ("user-001", "checking", 2500.75, now),
                ("user-001", "savings", 15000.00, now),
                ("user-002", "checking", 1200.50, now),
                ("user-002", "investment", 8500.25, now),
                ("user-003", "checking", 750.00, now)
            ]
            cursor.executemany(
                "INSERT INTO user_accounts (user_id, account_type, balance, created_at) VALUES (?, ?, ?, ?)",
                sample_accounts
            )

            # Insert sample transactions
            sample_transactions = [
                ("user-001", 1, -45.99, "debit", "Amazon", "Online purchase", "2025-08-21T09:30:00Z"),
                ("user-001", 1, -12.50, "debit", "Starbucks", "Coffee", "2025-08-21T08:15:00Z"),
                ("user-001", 1, 2000.00, "credit", "Employer", "Salary deposit", "2025-08-20T00:00:00Z"),
                ("user-002", 3, -85.20, "debit", "Grocery Store", "Weekly shopping", "2025-08-21T10:45:00Z"),
                ("user-002", 3, 500.00, "credit", "Freelance", "Project payment", "2025-08-19T14:30:00Z"),
                ("user-003", 5, -25.00, "debit", "Gas Station", "Fuel", "2025-08-21T07:20:00Z")
            ]
            cursor.executemany(
                """INSERT INTO user_transactions 
                   (user_id, account_id, amount, transaction_type, merchant, description, timestamp) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                sample_transactions
            )

            print("✅ Sample data inserted successfully")

        conn.commit()
        print(f"✅ Database initialized successfully at: {os.path.abspath(DB_PATH)}")

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        conn.rollback()
    finally:
        conn.close()

def log_audit_event(user_id: str, action: str, resource: str = None, details: str = None, 
                   ip_address: str = None, user_agent: str = None):
    """Log audit event to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        timestamp = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO audit_logs (timestamp, user_id, action, resource, details, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, user_id, action, resource, details, ip_address, user_agent))

        conn.commit()
        conn.close()
        print(f"📋 Audit: {action} by {user_id}")

    except Exception as e:
        print(f"❌ Audit logging error: {e}")

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
