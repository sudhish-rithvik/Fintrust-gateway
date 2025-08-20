from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes import accounts, transactions, loan, audit_log
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="FinTrust Gateway Backend",
    description="Backend API for FinTrust Gateway",
    version="1.0.0",
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routers
app.include_router(accounts.router, prefix="/api", tags=["Accounts"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])
app.include_router(loan.router, prefix="/api", tags=["Loan"])

# Include the new audit log router
app.include_router(audit_log.router, prefix="/api", tags=["Audit"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Add any additional startup or shutdown events if needed
