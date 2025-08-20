from fastapi import APIRouter, Depends
from auth import get_current_user, TokenPayload
from opa_policy import check_access
from audit_log.logger import log_event
from db import get_db_connection

router = APIRouter()

@router.get("/")
def get_transactions(user: TokenPayload = Depends(get_current_user)):
    # ✅ Step 1: Enforce Zero Trust with OPA
    check_access(
        user_id=user.sub,
        action="read",
        resource="transactions",
        roles=user.roles
    )

    # ✅ Step 2: Query transactions from DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, amount, merchant, timestamp 
        FROM user_transactions 
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user.sub,))
    rows = cursor.fetchall()
    conn.close()

    transactions = [
        {
            "id": row["id"],
            "amount": row["amount"],
            "merchant": row["merchant"],
            "timestamp": row["timestamp"]
        }
        for row in rows
    ]

    # ✅ Step 3: Audit log
    log_event(
        user_id=user.sub,
        action="read_transactions",
        details=f"User {user.preferred_username} accessed {len(transactions)} transactions",
        encrypted=False
    )

    return {"transactions": transactions}
