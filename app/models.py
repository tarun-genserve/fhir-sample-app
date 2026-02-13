from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    """OAuth2 token response model"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    scope: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
