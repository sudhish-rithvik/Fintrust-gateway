"""
Accounts API routes for FinTrust Gateway
Fixed version with proper error handling
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from auth import get_current_user, TokenPayload
from db_fixed import get_db_connection, log_audit_event
from typing import List, Dict, Any
from pydantic import BaseModel


router = APIRouter()

class Account(BaseModel):
    id: int
    user_id: str
    account_type: str
    balance: float
    created_at: str

class AccountSummary(BaseModel):
    total_accounts: int
    total_balance: float
    accounts: List[Account]

def check_account_access(user_id: str, action: str, resource: str = "accounts"):
    """Simple policy check for development"""
    # In development, allow all authenticated users to access their own data
    return True

@router.get("/accounts", response_model=AccountSummary)
async def get_user_accounts(
    request: Request,
    current_user: TokenPayload = Depends(get_current_user)
) -> AccountSummary:
    """
    Get all accounts for the authenticated user
    """
    try:
        # Policy check
        if not check_account_access(current_user.sub, "read", "accounts"):
            raise HTTPException(status_code=403, detail="Access denied")

        # Get accounts from database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_id, account_type, balance, created_at 
            FROM user_accounts 
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (current_user.sub,))

        rows = cursor.fetchall()
        conn.close()

        # Convert to Account objects
        accounts = [
            Account(
                id=row["id"],
                user_id=row["user_id"],
                account_type=row["account_type"],
                balance=row["balance"],
                created_at=row["created_at"]
            )
            for row in rows
        ]

        total_balance = sum(account.balance for account in accounts)

        # Audit log
        log_audit_event(
            user_id=current_user.sub,
            action="read_accounts",
            resource="accounts",
            details=f"Retrieved {len(accounts)} accounts",
            ip_address=getattr(request.client, 'host', None),
            user_agent=request.headers.get("user-agent")
        )

        return AccountSummary(
            total_accounts=len(accounts),
            total_balance=total_balance,
            accounts=accounts
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving accounts: {str(e)}"
        )

@router.get("/accounts/{account_id}")
async def get_account_details(
    account_id: int,
    request: Request,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Get details for a specific account
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify account belongs to user
        cursor.execute("""
            SELECT id, user_id, account_type, balance, created_at 
            FROM user_accounts 
            WHERE id = ? AND user_id = ?
        """, (account_id, current_user.sub))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Account not found")

        account = Account(
            id=row["id"],
            user_id=row["user_id"],
            account_type=row["account_type"],
            balance=row["balance"],
            created_at=row["created_at"]
        )

        # Audit log
        log_audit_event(
            user_id=current_user.sub,
            action="read_account_details",
            resource=f"account:{account_id}",
            details=f"Retrieved account {account_id}",
            ip_address=getattr(request.client, 'host', None),
            user_agent=request.headers.get("user-agent")
        )

        return account

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving account: {str(e)}"
        )

@router.get("/accounts/summary")
async def get_accounts_summary(
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Get a quick summary of all accounts
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                account_type,
                COUNT(*) as count,
                SUM(balance) as total_balance,
                AVG(balance) as avg_balance
            FROM user_accounts 
            WHERE user_id = ?
            GROUP BY account_type
        """, (current_user.sub,))

        rows = cursor.fetchall()
        conn.close()

        summary = {
            "by_type": [
                {
                    "account_type": row["account_type"],
                    "count": row["count"],
                    "total_balance": row["total_balance"],
                    "average_balance": row["avg_balance"]
                }
                for row in rows
            ],
            "total_balance": sum(row["total_balance"] for row in rows),
            "total_accounts": sum(row["count"] for row in rows)
        }

        return summary

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )
