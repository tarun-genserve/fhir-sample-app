from fastapi import APIRouter, HTTPException
from app.services.epic_auth import obtain_epic_token
from app.models import TokenResponse

router = APIRouter()

@router.post("/token", response_model=TokenResponse)
async def auth_token():
    """
    OAuth2 token endpoint that:
    1. Builds a JWT client assertion signed with your private key
    2. Sends the assertion to Epic's token endpoint
    3. Returns the access token

    The access token can then be used to make FHIR API requests to Epic.
    """
    try:
        token_data = await obtain_epic_token()
        return token_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to obtain token: {str(e)}")
