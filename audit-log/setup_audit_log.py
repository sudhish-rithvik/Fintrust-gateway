# audit-log/setup_audit_log.py

import sqlite3

DB_PATH = "audit_log.db"

def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_id TEXT,
            action TEXT NOT NULL,
            details TEXT,
            encrypted BOOLEAN DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database '{DB_PATH}' created with audit_logs table.")

if __name__ == "__main__":
    create_db()
