from fastapi import APIRouter, HTTPException, Request, Depends
import httpx
import os
from auth import get_current_user, TokenPayload
from opa_policy import check_access
from audit_log.logger import log_event

router = APIRouter()

# URL of the encryption service (from .env or default Docker host)
ENCRYPTION_API = os.getenv("ENCRYPTION_API", "http://encryption-service:5000")

@router.post("/evaluate")
async def evaluate_loan(request: Request, user: TokenPayload = Depends(get_current_user)):
    # ✅ Step 1: Check policy via OPA
    check_access(
        user_id=user.sub,
        action="loan_evaluation",
        resource="loan",
        roles=user.roles
    )

    # ✅ Step 2: Extract the encrypted payload
    try:
        payload = await request.json()
        encrypted_payload = payload.get("encrypted_payload")
        if not encrypted_payload:
            raise HTTPException(status_code=400, detail="Missing encrypted_payload in request body.")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON request")

    # ✅ Step 3: Call Flask HE service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{ENCRYPTION_API}/loan/evaluate", json={"encrypted_payload": encrypted_payload})

        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Encryption service error")

        encrypted_result = response.json().get("encrypted_loan_result")
        if not encrypted_result:
            raise HTTPException(status_code=500, detail="Missing encrypted loan result from HE service")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Loan evaluation failed: {str(e)}")

    # ✅ Step 4: Log the event
    log_event(
        user_id=user.sub,
        action="loan_evaluation",
        details=f"Loan evaluated for user {user.preferred_username} using homomorphic encryption",
        encrypted=True
    )

    # ✅ Step 5: Return result
    return {"encrypted_loan_result": encrypted_result}
