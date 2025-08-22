"""
Authentication module for FinTrust Gateway
Simplified for local development (no Keycloak dependency)
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import jwt
import os
from datetime import datetime, timedelta

# Simple JWT configuration for development
SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: str
    email: Optional[str] = None
    preferred_username: Optional[str] = None
    roles: List[str] = []
    exp: Optional[int] = None

class User(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str] = ["user"]

# Mock user database for development
MOCK_USERS = {
    "user-001": User(user_id="user-001", username="john_doe", email="john@example.com", roles=["user", "account_reader"]),
    "user-002": User(user_id="user-002", username="jane_smith", email="jane@example.com", roles=["user", "premium"]),
    "user-003": User(user_id="user-003", username="bob_wilson", email="bob@example.com", roles=["user"]),
    "admin": User(user_id="admin", username="admin", email="admin@fintrust.com", roles=["admin", "user"])
}

def create_access_token(user_id: str, additional_claims: dict = None) -> str:
    """Create JWT access token for development"""
    user = MOCK_USERS.get(user_id)
    if not user:
        raise ValueError("User not found")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user.user_id,
        "preferred_username": user.username,
        "email": user.email,
        "roles": user.roles,
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "fintrust-dev"
    }

    if additional_claims:
        payload.update(additional_claims)

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> TokenPayload:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(
            sub=payload["sub"],
            email=payload.get("email"),
            preferred_username=payload.get("preferred_username"),
            roles=payload.get("roles", []),
            exp=payload.get("exp")
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenPayload:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    return decode_token(token)

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[TokenPayload]:
    """Get current user if authenticated, otherwise None"""
    if not credentials:
        return None
    return decode_token(credentials.credentials)

def require_roles(required_roles: List[str]):
    """Dependency to require specific roles"""
    def role_checker(current_user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not any(role in current_user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return current_user
    return role_checker

# Development login endpoint
from fastapi import APIRouter

auth_router = APIRouter()

@auth_router.post("/login")
async def dev_login(user_id: str):
    """Development login endpoint - generates token for any valid user_id"""
    if user_id not in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    token = create_access_token(user_id)
    user = MOCK_USERS[user_id]

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles
        }
    }

@auth_router.get("/users")
async def get_available_users():
    """Development endpoint - list available users for testing"""
    return {
        "available_users": [
            {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles
            }
            for user in MOCK_USERS.values()
        ],
        "instructions": "POST /auth/login with user_id to get a token"
    }

# Export the router to include in main app
def get_auth_router():
    return auth_router
