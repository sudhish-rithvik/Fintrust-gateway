from fastapi import APIRouter, Depends
from auth import get_current_user, TokenPayload
from opa_policy import check_access
from audit_log.logger import log_event
from db import get_db_connection

router = APIRouter()

@router.get("/")
def get_accounts(user: TokenPayload = Depends(get_current_user)):
    # ✅ Step 1: Enforce ZTA with OPA
    check_access(
        user_id=user.sub,
        action="read",
        resource="accounts",
        roles=user.roles
    )

    # ✅ Step 2: Connect to DB and fetch real accounts
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, account_type, balance FROM user_accounts WHERE user_id = ?", (user.sub,))
    rows = cursor.fetchall()
    conn.close()

    accounts = [
        {"id": row["id"], "type": row["account_type"], "balance": row["balance"]}
        for row in rows
    ]

    # ✅ Step 3: Audit log
    log_event(
        user_id=user.sub,
        action="read_accounts",
        details=f"User {user.preferred_username} accessed accounts ({len(accounts)} records)",
        encrypted=False
    )

    return {"accounts": accounts}
