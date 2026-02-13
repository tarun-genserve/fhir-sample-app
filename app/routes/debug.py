from fastapi import APIRouter
from app.services.epic_auth import build_client_assertion
from app.config import settings
import jwt
import os
from pathlib import Path

router = APIRouter()

@router.get("/debug/jwt")
async def debug_jwt():
    """
    Debug endpoint to inspect the JWT assertion being generated.
    Shows the JWT payload, headers, and configuration.
    """
    assertion = await build_client_assertion()

    # Decode without verification to inspect payload and headers
    decoded_payload = jwt.decode(assertion, options={"verify_signature": False})
    decoded_header = jwt.get_unverified_header(assertion)

    # Calculate expiration time
    from datetime import datetime
    exp_time = datetime.fromtimestamp(decoded_payload.get('exp', 0))

    return {
        "jwt_assertion": assertion,
        "decoded_header": decoded_header,
        "decoded_payload": decoded_payload,
        "expiration_utc": exp_time.isoformat(),
        "config": {
            "client_id": settings.EPIC_CLIENT_ID,
            "kid": settings.EPIC_JWT_KID or "(not configured)",
            "token_endpoint": settings.EPIC_TOKEN_ENDPOINT,
            "key_path": settings.EPIC_PRIVATE_KEY_PATH
        }
    }

@router.get("/debug/public-key")
async def get_public_key():
    """
    Returns your public key that needs to be registered with Epic.
    Copy this and paste it into your Epic FHIR application configuration.
    """
    # Find the public key file
    key_path = settings.EPIC_PRIVATE_KEY_PATH
    if not os.path.isabs(key_path):
        project_root = Path(__file__).parent.parent.parent
        key_dir = (project_root / key_path).parent
    else:
        key_dir = Path(key_path).parent

    # Try common public key names
    public_key_path = None
    for name in ["publickey.pem", "public.pem", "public_key.pem"]:
        candidate = key_dir / name
        if candidate.exists():
            public_key_path = candidate
            break

    if not public_key_path:
        return {"error": "Public key not found", "searched_in": str(key_dir)}

    with open(public_key_path, "r") as f:
        public_key = f.read()

    return {
        "public_key": public_key,
        "instructions": "Copy the public_key value above and register it with Epic at their FHIR sandbox portal",
        "client_id": settings.EPIC_CLIENT_ID,
        "kid": settings.EPIC_JWT_KID or "(not configured - optional)"
    }

@router.post("/debug/token-request")
async def debug_token_request():
    """
    Debug endpoint that shows the exact request being sent to Epic
    without actually sending it (useful for debugging).
    """
    assertion = await build_client_assertion()

    data = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": assertion[:50] + "...",  # Truncate for display
        "scope": "system/*.read"
    }

    return {
        "endpoint": settings.EPIC_TOKEN_ENDPOINT,
        "method": "POST",
        "data": data,
        "note": "client_assertion is truncated for display"
    }
