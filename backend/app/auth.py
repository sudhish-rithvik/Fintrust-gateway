import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

# Environment/config
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
REALM = os.getenv("KEYCLOAK_REALM", "fintrust")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "kong-client")

# JWKS URI
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenPayload(BaseModel):
    sub: str
    email: str = None
    preferred_username: str = None
    roles: list = []

# Cache JWKS
jwks_cache = {}

def get_jwks():
    global jwks_cache
    if not jwks_cache:
        response = requests.get(JWKS_URL)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch JWKS")
        jwks_cache = response.json()
    return jwks_cache

def decode_token(token: str):
    jwks = get_jwks()
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Missing 'kid' in token header")

    key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
    if not key:
        raise HTTPException(status_code=401, detail="Public key not found")

    try:
        public_key = jwt.construct_rsa_public_key(key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[key["alg"]],
            audience=CLIENT_ID,
            options={"verify_exp": True}
        )
        return TokenPayload(
            sub=payload["sub"],
            email=payload.get("email"),
            preferred_username=payload.get("preferred_username"),
            roles=payload.get("realm_access", {}).get("roles", [])
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    return decode_token(token)
