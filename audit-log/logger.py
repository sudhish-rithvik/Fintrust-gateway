# audit-log/logger.py

import sqlite3
import datetime

DB_PATH = "audit-log/audit_log.db"

def log_event(user_id: str, action: str, details: str, encrypted=False):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        timestamp = datetime.datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO audit_logs (timestamp, user_id, action, details, encrypted)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, user_id, action, details, int(encrypted)))

        conn.commit()
        conn.close()
        print(f"[AUDIT LOG] {timestamp} - {action} - {user_id}")
    except Exception as e:
        print(f"[ERROR] Failed to write to audit log: {str(e)}")
