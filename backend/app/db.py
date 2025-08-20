# backend/app/db.py
import sqlite3

DB_PATH = "audit-log/audit_log.db"  # Or use a .env var for production DB

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

