import jwt
import requests
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from app.config import settings

async def build_client_assertion():
    """
    Build a JWT assertion signed with the private key according to Epic backend OAuth2 spec.

    This follows the SMART Backend Services specification:
    - The JWT must be signed with RS384 algorithm
    - The private key must match the public key registered with Epic
    - The JWT contains claims identifying the client and the intended audience

    Required settings:
    - EPIC_CLIENT_ID: Your application's client ID from Epic
    - EPIC_PRIVATE_KEY_PATH: Path to your RS384 private key file
    - EPIC_TOKEN_ENDPOINT: The Epic token endpoint URL (used as audience)

    Optional settings:
    - EPIC_JWT_KID: Key ID to include in JWT header (for JWKS lookup)

    Returns:
        str: The encoded JWT assertion
    """
    # Load the private key from file
    # This should be an RS384 private key that matches the public key you registered with Epic
    # Handle relative paths by resolving from project root
    key_path = settings.EPIC_PRIVATE_KEY_PATH
    if not os.path.isabs(key_path):
        # Resolve relative to project root (parent of app directory)
        project_root = Path(__file__).parent.parent.parent
        key_path = project_root / key_path

    with open(key_path, "rb") as f:
        private_key = f.read()

    now = datetime.now(timezone.utc)

    # Build JWT payload according to Epic's requirements
    payload = {
        "iss": settings.EPIC_CLIENT_ID,  # Issuer: your client ID
        "sub": settings.EPIC_CLIENT_ID,  # Subject: your client ID
        "aud": settings.EPIC_TOKEN_ENDPOINT,  # Audience: Epic's token endpoint
        "iat": int(now.timestamp()),  # Issued at time
        "exp": int((now + timedelta(minutes=5)).timestamp()),  # Expiration (5 minutes)
        "jti": f"{settings.EPIC_CLIENT_ID}-{now.timestamp()}"  # Unique token ID
    }

    # Build JWT headers
    headers = {
        "alg": "RS384",
        "typ": "JWT"
    }

    # Include kid (key ID) if configured - recommended for JWKS-based key management
    if settings.EPIC_JWT_KID:
        headers["kid"] = settings.EPIC_JWT_KID

    # Sign the JWT with RS384 algorithm as required by Epic
    assertion = jwt.encode(
        payload,
        private_key,
        algorithm="RS384",
        headers=headers
    )

    # Ensure assertion is a string (not bytes) for compatibility
    if isinstance(assertion, bytes):
        assertion = assertion.decode('utf-8')

    return assertion

async def obtain_epic_token():
    """
    Request an access token from Epic using the client_credentials grant type
    with a JWT client assertion.

    This implements the SMART Backend Services authorization flow:
    1. Build a signed JWT assertion
    2. POST to Epic's token endpoint with the assertion
    3. Receive an access token that can be used for FHIR API calls

    The scope requested is "system/*.read" which allows read access to all resource types.
    You can modify this scope based on your application's needs.

    Returns:
        dict: Token response containing access_token, token_type, expires_in, and scope

    Raises:
        requests.HTTPError: If the token request fails
    """
    # Build the signed JWT assertion
    assertion = await build_client_assertion()

    # Prepare the token request data according to OAuth2 spec
    data = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": assertion,
        "scope": "system/*.read"  # Modify scope based on your needs
    }

    # Request the token from Epic with timeout
    response = requests.post(
        settings.EPIC_TOKEN_ENDPOINT,
        data=data,
        timeout=30
    )

    # If request fails, provide detailed error for debugging
    if response.status_code != 200:
        try:
            error_detail = response.json()
        except:
            error_detail = response.text

        # Provide helpful debugging hints
        error_msg = (
            f"Epic token error {response.status_code}: {error_detail}. "
            "\nDebugging tips:"
            "\n- Verify EPIC_CLIENT_ID matches your Epic application registration"
            "\n- Ensure public key is uploaded to Epic and matches your private key"
            "\n- Check if JWT 'kid' header matches Epic JWKS configuration"
            "\n- Verify JWT signature algorithm is RS384"
            "\n- Confirm token endpoint URL is correct"
        )
        raise Exception(error_msg)

    # Parse and return the token response
    result = response.json()
    return {
        "access_token": result.get("access_token"),
        "token_type": result.get("token_type", "Bearer"),
        "expires_in": result.get("expires_in"),
        "scope": result.get("scope")
    }
