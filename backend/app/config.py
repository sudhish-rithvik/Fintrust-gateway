# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # General app settings
    app_name: str = "FinTrust Gateway Backend"
    environment: str = "development"
    debug: bool = True

    # API Settings
    api_prefix: str = "/api"

    # OAuth2 / Auth settings
    oauth2_client_id: str = "kong-client"
    oauth2_client_secret: str = "kong-secret"
    token_url: str = "http://localhost:18000/oauth2/token"

    # Logging and audit settings
    audit_log_path: str = "./audit_log/logs.json"

    # Encryption service URL
    encryption_service_url: str = "http://encryption-service:5000"

    # Allowed CORS origins
    cors_origins: list[str] = ["http://localhost:3000"]

settings = Settings()
