"""
FinTrust Gateway - Main FastAPI Application
Fixed version for local development
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from routes import accounts, transactions, loan, audit_log
from auth import get_auth_router  # ADD THIS
from db import init_database
import os

# Initialize FastAPI app
app = FastAPI(
    title="FinTrust Gateway Backend",
    description="Secure FinTech API Gateway with Authentication & Encryption",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS settings for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router (IMPORTANT!)
app.include_router(get_auth_router(), prefix="/auth", tags=["Authentication"])

# Include API routers
app.include_router(accounts.router, prefix="/api/v1", tags=["Accounts"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(loan.router, prefix="/api/v1", tags=["Loan"])
app.include_router(audit_log.router, prefix="/api/v1", tags=["Audit"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "FinTrust Gateway Backend",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to FinTrust Gateway API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "login": "/auth/login"
    }

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "path": str(request.url)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting FinTrust Gateway Backend...")
    init_database()
    print("✅ Database initialized successfully")
    print("📖 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    print("🏃 Running FinTrust Gateway in development mode...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
