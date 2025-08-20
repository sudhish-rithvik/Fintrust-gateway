from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AuditLog(BaseModel):
    action: str
    status: str

@router.post("/audit", tags=["Audit"])
async def log_audit(log: AuditLog):
    # For now, just log to console
    print(f"[AUDIT] Action: {log.action}, Status: {log.status}")
    return {"message": "Audit log received"}
