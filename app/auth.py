import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = os.environ.get("API_KEY", "f1-api-key")

api_key_header = APIKeyHeader(name="X-API-Key", description="API key required for write operations")


def require_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
