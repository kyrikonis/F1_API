import os
import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable must be set")

api_key_header = APIKeyHeader(name="X-API-Key", description="API key required for write operations")


def require_api_key(key: str = Security(api_key_header)):
    if not secrets.compare_digest(key.encode(), API_KEY.encode()):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
