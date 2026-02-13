import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Configuration settings loaded from environment variables.

    Required environment variables:
    - EPIC_CLIENT_ID: Your Epic FHIR application client ID
    - EPIC_PRIVATE_KEY_PATH: Path to your private key file (RS384) for JWT signing

    Optional environment variables:
    - EPIC_TOKEN_ENDPOINT: Epic OAuth2 token endpoint (defaults to sandbox)
    - EPIC_JWT_KID: Key ID for JWKS (recommended for key rotation)
    """
    def __init__(self):
        self.EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID")
        self.EPIC_PRIVATE_KEY_PATH = os.getenv("EPIC_PRIVATE_KEY_PATH")
        self.EPIC_TOKEN_ENDPOINT = os.getenv(
            "EPIC_TOKEN_ENDPOINT",
            "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
        )
        self.EPIC_JWT_KID = os.getenv("EPIC_JWT_KID")  # Optional key ID for JWKS

settings = Settings()
